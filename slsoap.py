# ~*~ coding: utf-8 ~*~

"""
sloap.soapClient
~~~~~~~~~~~~~~~~

This module provides a SOAP client interface to
SoftLayer's API.

See included example.py for usage.

"""


import suds
from suds.client import Client
from suds.sax.element import Element
from suds.xsd.doctor import ImportDoctor, Import

"""Class for connecting with the SoftLayer API via SOAP (requires suds)"""
class soapClient:

	def __init__(self,object_type,object_id,api_user,api_key):
		"""
		Initializes the client - sets up the:
			request URL 
			API user/key 
			Default object filter/mask
			Default limit/offset
		"""
		self.api_base_url 	= 'https://api.softlayer.com/soap/v3/'
		self.api_user		= api_user
		self.api_key		= api_key

		d 					= ImportDoctor( Import( "http://schemas.xmlsoap.org/soap/encoding/" ) )
		self.request_url 	= self.api_base_url+object_type+'?wsdl'
		self.client 		= Client(self.request_url,doctor=d,cache=None,xstq=False,faults=False)
		self.ims_ns			= ('ns2','http://api.service.softlayer.com/soap/v3/')
		self.object_type	= object_type.strip()

		self.object_filter  = Element('%sObjectFilter' % object_type,ns=self.ims_ns)
		self.object_mask 	= Element('%sObjectMask' % object_type,ns=self.ims_ns)
		self.limit 			= 10
		self.offset 		= 0
		self.result_limit 	= None

	def build_soap_header(self,el,data):
		"""Set up a SOAP object for our headers"""
		## make our first element
		for name in data:
			if(type(data[name]) is dict):
				## append to the current element
				nel = Element(name)
				el.children.append(nel)
				self.build_soap_header(nel,data[name])
			else:
				opt = Element(name)
				opt.setText(data[name])
				el.children.append(opt)
				#print "{name} - {data}".format(name=name,data=data[name])

		return el

	def set_object_mask(self,data):
		"""Create an object mask to tell the API what we want"""
		print '%sObjectMask' % self.object_type
		el = Element('%sObjectMask' % self.object_type,ns=self.ims_ns)
		mask = Element('mask')
		mask = self.build_soap_header(mask,data)
		el.children = [mask]
		return el

	def set_object_filter(self,data):
		"""Create an object filter to limit our results"""
		object_filter = Element('%sObjectFilter' % self.object_type,ns=self.ims_ns)
		return self.build_soap_header(object_filter,data)

	def set_result_limit(self,limit,offset):
		"""Set the limit and offset for a number of results to return"""
		result_limit = Element('resultLimit',ns=self.ims_ns)
		result_limit = self.build_soap_header(result_limit,{
			'limit'  : limit,
			'offset' : offset
		})
		return result_limit

	def set_auth_header(self):
		"""Set up the authorization header"""
		auth_user   = Element('username').setText(self.api_user)
		auth_key    = Element('apiKey').setText(self.api_key)
		auth_header = Element('authenticate',ns=self.ims_ns)
		auth_header.children = [auth_user,auth_key]
		return auth_header

	def __getattr__(self,name):
		print 'calling %s' % name
		try:
			return object.__getattr__(self, name)
		except AttributeError:
			print 'not found - trying: %s' % name

			def call_handler(*args, **kwargs):
				"""
				Place a SoftLayer API call
				"""

				auth_header  = self.set_auth_header()
				result_limit = self.set_result_limit(self.limit,self.offset)

				print auth_header
				print result_limit
				print self.object_mask
				print self.object_filter

				self.client.set_options(soapheaders=[auth_header,self.object_filter,self.object_mask,result_limit])

				try:
					result = self.client.service.__getattr__(name)(args)
					return result

				except suds.WebFault,e:
					print 'ERROR: %s' % e

            	return call_handler

