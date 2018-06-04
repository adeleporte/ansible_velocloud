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
module: enterprise
short_description: Manage your Velocloud Enterprises
'''


EXAMPLES = '''
    - name: Create Velocloud Enterprise
      no_log: true
      enterprise:
        host: "172.18.7.200"
        user: "super@velocloud.net"
        password: "vcadm!n"
        enterprise_name: "{{ item }}"
        state: present
      with_items:
        - "test-ansible1"
        - "test-ansible2"
      register: result

    - name: Delete Velocloud Enterprise
      no_log: true
      enterprise:
        host: "172.18.7.200"
        user: "super@velocloud.net"
        password: "vcadm!n"
        enterprise_name: "test-ansible"
        state: absent
      register: result
'''

from ansible.module_utils.basic import *
from uuid import uuid4

import velocloud
from velocloud.rest import ApiException
import urllib3


def create_enterprise(host, user, password, name):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl = False
    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = None

    UNIQ = str(uuid4())
    params = {"name": name,
              "networkId": 1,
              "configurationId": 6,
              "user": {"username": "%s@velocloud.net" % UNIQ, "password": "testsecr3t"},
              "enableEnterpriseDelegationToOperator": True,
              "enableEnterpriseUserManagementDelegationToOperator": True}
    try:
        res = api.enterpriseInsertEnterprise(params)
        return res.id
    except ApiException as e:
        module.exit_json(changed=False, argument_spec=module.params, result="Entreprise was not created")


def get_enterprise(host, user, password, name):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl=False

    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = None

    try:
        res = api.enterpriseGetEnterprise({ "name": name })
        return res.id
    except:
        return None


def delete_enterprise(host, user, password, id):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl=False

    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = None

    try:
        res = api.enterpriseDeleteEnterprise({ "enterpriseId": id })
        return res.id
    except:
        return None


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
    if not id:
        # Enterprise doesn't exist with this name, let's create it
        if module.params['state'] == 'present':
            create_result = create_enterprise(host, user, password, enterprise)
            module.exit_json(changed=True, argument_spec=module.params, entreprise_id=create_result)
        else:
            module.exit_json(changed=False, argument_spec=module.params)

    if module.params['state'] == 'absent':
        # Delete Enterprise
        delete_enterprise(host, user, password, id)
        module.exit_json(changed=True, argument_spec=module.params, entreprise_id=id)
    else:
        # Just return ID
        module.exit_json(changed=False, argument_spec=module.params, entreprise_id=id)

if __name__ == '__main__':
    main()

