from __future__ import print_function

from uuid import uuid4

import velocloud
from velocloud.rest import ApiException

# If SSL verification disabled (e.g. in a development environment)
import urllib3
urllib3.disable_warnings()
velocloud.configuration.verify_ssl=False

client = velocloud.ApiClient(host="172.18.7.200")
client.authenticate("super@velocloud.net", "vcadm!n", operator=True)
api = velocloud.AllApi(client)

UNIQ = str(uuid4())


# 3. Provision a Gateway
#
result = { "id": 0,
           "activationKey": 0 }



print("### PROVISIONING EDGE ###")
params = { "ipAddress": "1.1.1.1",
           "name": "gateway-ansible",
           "description": "A test Gateway generated with Ansible",
           "networkId": 1,
           "gatewayPoolId": 1 }
try:
    gateway = api.gatewayGatewayProvision(params)
    result["id"] = gateway.id
    result["activationKey"] = gateway.activationKey
    print(result)
except ApiException as e:
    print(e)


try:
    res = api.networkGetNetworkGateways({"networkId": 1})
    for gateway in res:
        if gateway.name == "gateway-ansible":
            break
        result["id"] = gateway.id
        result["activationKey"] = gateway.activationKey
    print( result )

except ApiException as e:
    print(e)

res = api.gatewayDeleteGateway({"id": gateway.id})
print( res.id )