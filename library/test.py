#!/usr/bin/python
# coding=utf-8

__author__ = 'adeleporte'



from uuid import uuid4

import velocloud
from velocloud.rest import ApiException
import urllib3
import sys
import json


def get_enterprise(host, user, password, name):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl=False

    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = []


    try:
        res.append(api.enterpriseGetEnterprise({ "name": name }))
        return res
    except velocloud.ApiException as e:
        return None


from ansible.module_utils.basic import *
def main():
    fields = {
        "host": {"required": True, "type": "str"},
        "user": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "enterprise_name": {"required": True, "type": "str"},
        "state": dict(default='present', choices=['present', 'absent'])
    }
    module = AnsibleModule(argument_spec=fields)

    host = module.params['host']
    user = module.params['user']
    password = module.params['password']
    enterprise = module.params['enterprise_name']

    id = get_enterprise(host, user, password, enterprise)
    module.exit_json(changed=False, argument_spec=module.params, meta=id)


if __name__ == '__main__':
    main()

