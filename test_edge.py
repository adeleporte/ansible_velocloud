from __future__ import print_function

from uuid import uuid4

import velocloud
from velocloud.rest import ApiException

# If SSL verification disabled (e.g. in a development environment)
import urllib3
urllib3.disable_warnings()
velocloud.configuration.verify_ssl=False

client = velocloud.ApiClient(host="172.16.65.168")
client.authenticate("super@velocloud.net", "vcadm!n", operator=True)
api = velocloud.AllApi(client)


res = None
gateway = None
result = {"id": 0, "activationKey": 0}

res = api.enterpriseGetEnterpriseEdges({"enterpriseId": 3})
for edge in res:
  if edge.name == "test":
    result["id"] = edge.id
    result["activationKey"] = edge.activationKey
    print (result)


#
# 3. Provision an Edge
#
print("### PROVISIONING EDGE ###")
params = { "enterpriseId": 3,
           "name": "SDKTestCo Branch 1",
           "description": "A test Edge generated with the VeloCloud Python SDK",
           "modelNumber": "virtual",
           "configurationId": 20 }
try:
    res = api.edgeEdgeProvision(params)
    print(res)
except ApiException as e:
    print(e)


