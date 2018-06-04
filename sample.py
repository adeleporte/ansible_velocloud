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

#
# 1. Insert a new enterprise
#
print("### CREATING NEW ENTERPRISE ###")
params = { "name": "SDKTestCo " + UNIQ,
           "networkId": 1,
           "configurationId": 6,
           "user": { "username": "%s@velocloud.net" % UNIQ, "password": "testsecr3t" },
           "enableEnterpriseDelegationToOperator": True,
           "enableEnterpriseUserManagementDelegationToOperator": True }
try:
    res = api.enterpriseInsertEnterprise(params)
    print(res)
except ApiException as e:
    print(e)

enterpriseId = res.id

#
# 1.5. Get enterprise network service
#
print("### GETTING ENTERPRISE CONFIGURATIONS ###")
params = { "enterpriseId": enterpriseId }
try:
    res = api.enterpriseGetEnterpriseServices(params)
    print(res)
except ApiException as e:
    print(e)




#
# 2. Get enterprise profiles
#
print("### GETTING ENTERPRISE CONFIGURATIONS ###")
params = { "enterpriseId": enterpriseId }
try:
    res = api.enterpriseGetEnterpriseConfigurations(params)
    print(res)
except ApiException as e:
    print(e)

profileId = res[0].id

#
# 3. Provision an Edge
#
print("### PROVISIONING EDGE ###")
params = { "enterpriseId": enterpriseId,
           "name": "SDKTestCo Branch 1",
           "description": "A test Edge generated with the VeloCloud Python SDK",
           "modelNumber": "edge500",
           "configurationId": profileId }
try:
    res = api.edgeEdgeProvision(params)
    print(res)
except ApiException as e:
    print(e)


"""
Using models
============

A second means of passing parameters is to rely on the models defined in
velocloud/models/. These models are provided for convenience and support
Python-native introspection (e.g. via the dir() function).

Models are defined for each request and response object, as well as ancillary
objects (e.g. enterprises, edges, etc.) which are shared across API methods.
Model names are consistent with the Swagger documentation included in the SDK
package.

"""

#
# 4. Insert a second enterprise
#
print("### CREATING ANOTHER NEW ENTERPRISE (MODELS) ###")
req = velocloud.EnterpriseInsertEnterprise(name="SDKTestInc " + UNIQ,
                                           networkId=1,
                                           configurationId=1,
                                           enableEnterpriseDelegationToOperator=True,
                                           enableEnterpriseUserManagementDelegationToOperator=True)
req.user = velocloud.AuthObject(username=("%s.2@velocloud.net" % UNIQ), password="testsecr3t")
try:
    res = api.enterpriseInsertEnterprise(req)
    print(res)
except ApiException as e:
    print(e)

enterpriseId = res.id

#
# 5. Get enterprise profiles
#
print("### GETTING ENTERPRISE CONFIGURATIONS (MODELS) ###")
req = velocloud.EnterpriseGetEnterpriseConfigurations(enterpriseId=enterpriseId)
try:
    res = api.enterpriseGetEnterpriseConfigurations(req)
    print(res)
except ApiException as e:
    print(e)

profileId = res[0].id

#
# 6. Provision an Edge
#
print("### PROVISIONING EDGE (MODELS) ###")
req = velocloud.EdgeEdgeProvision(enterpriseId=enterpriseId,
                                  configurationId=profileId,
                                  name="SDKTestInc Branch 1",
                                  description="A test Edge generated with the VeloCloud Python SDK models",
                                  modelNumber="edge500")
try:
    res = api.edgeEdgeProvision(req)
    print(res)
except ApiException as e:
    print(e)
