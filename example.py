"""Test using the SLSoap module"""

import slsoap

api_key	 	 = 'YOUR_API_KEY'
api_user 	 = 'YOUR_API_USER'
hostname  	 = 'YOUR_HARDWARE_HOSTNAME'

sl = slsoap.soapClient('SoftLayer_Account',None,api_user,api_key)

sl.object_mask = sl.set_object_mask({
	'tickets' : {
		'attachedHardware' : {
			'networkComponents' : {}
		}
	}
})

sl.object_filter = sl.set_object_filter({
	'tickets' : {
		'attachedHardware' : {
			'hostname' : {
				'operation' : hostname
			}
		}
	}
})

print '### RESULT:'
print sl.getTickets()
