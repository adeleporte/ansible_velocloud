#!/usr/bin/python
# coding=utf-8
#
# Copyright © 2018 VMware, Inc. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions
# of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
__author__ = 'adeleporte'


DOCUMENTATION = '''
---
module: profile
short_description: Manage your Velocloud Profile
'''


EXAMPLES = '''

'''

from ansible.module_utils.basic import *
from uuid import uuid4

import velocloud
from velocloud.rest import ApiException
import urllib3


def create_profile(host, user, password, name, description, enterprise_id):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl = False
    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = None
    result = {"id": 0}

    params = {"name": name,
              "description": description,
              "enterpriseId": enterprise_id}
    try:
        res = api.configurationCloneEnterpriseTemplate(params)
        result["id"] = res.id
        return result
    except Exception as e:
        module.exit_json(changed=False, result="Profile was not created")


def get_profile(host, user, password, profile_name, enterprise_id):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl=False

    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = None


    try:
        res = api.enterpriseGetEnterpriseConfigurations({"enterpriseId": enterprise_id})
        for profile in res:
            if profile.name == profile_name:
                return profile.id
        return None
    except ApiException as e:
        module.exit_json(changed=False, result="Failed to get any profile")



def delete_profile(host, user, password, enterprise_id, profile_id):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl=False

    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = None

    params = {"enterpriseId": enterprise_id, "id": profile_id}

    try:
        res = api.configurationDeleteConfiguration(params)
        return res
    except:
        return None


def main():
    fields = {
        "host": {"required": True, "type": "str"},
        "user": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "profile_name": {"required": False, "default": "Quick Start Profile", "type": "str"},
        "description": {"required": False, "type": "str"},
        "enterprise_id": {"required": True, "type": "int"},
        "state": dict(default='present', choices=['present', 'absent'])
    }
    module = AnsibleModule(argument_spec=fields)

    host = module.params['host']
    user = module.params['user']
    password = module.params['password']
    description = module.params['description']
    enterprise_id = module.params['enterprise_id']
    profile_name = module.params['profile_name']

    profile = get_profile(host, user, password, profile_name, enterprise_id)
    if not profile:
        # Profile doesn't exist with this name, let's create it
        if module.params['state'] == 'present':
            create_result = create_profile(host, user, password, profile_name, description, enterprise_id)
            module.exit_json(changed=True, argument_spec=module.params, profile_id=create_result["id"])
        else:
            module.exit_json(changed=False, argument_spec=module.params, profile_id=0)

    if module.params['state'] == 'absent':
        # Delete Profile
        delete_profile(host, user, password, enterprise_id, profile)
        module.exit_json(changed=True, argument_spec=module.params, profile_id=profile)
    else:
        # Just return ID
        module.exit_json(changed=False, argument_spec=module.params, profile_id=profile)

if __name__ == '__main__':
    main()

