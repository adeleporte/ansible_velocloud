from __future__ import print_function
from uuid import uuid4
from copy import deepcopy

import velocloud
from velocloud.rest import ApiException
from velocloud.models import *
from velocloud.configuration import *

# If SSL verification disabled (e.g. in a development environment)
import urllib3
urllib3.disable_warnings()
velocloud.configuration.verify_ssl=False

client = velocloud.ApiClient(host="172.16.65.168")
client.authenticate("super@velocloud.net", "vcadm!n", operator=True)
api = velocloud.AllApi(client)


#
# Clone configuration profile
#
print("### GET EDGE CONFIGURATIONS ###")
params = { "edgeId": 62,
            "enterpriseId": 6,
            "with": "modules"
           }
try:
    configurations = api.edgeGetEdgeConfigurationStack(params)
    #print (configurations)
except ApiException as e:
    print(e)


configuration = configurations[0]
print (configuration.id)


device_module = None
for module in configuration.modules:
    if module.name == "deviceSettings":
        device_module = module
        break


settings = device_module.data["routedInterfaces"][1]
#print (settings)

new_settings = deepcopy(settings)
new_settings["wanOverlay"] = "USER_DEFINED"
#print (new_settings)


device_module.data["routedInterfaces"][1]["override"] = "true"
device_module.data["routedInterfaces"][1]["wanOverlay"] = "USER_DEFINED"
print (device_module)

try:
    result = api.configurationUpdateConfigurationModule({ "id": device_module.id, "enterpriseId": 6, "_update": device_module })
    print (result)

except ApiException as e:
    print ("Error in configuration_update_configuration_module")
    print (e)




