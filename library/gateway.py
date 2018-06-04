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
module: gateway
short_description: Manage your Velocloud Gateways
'''


EXAMPLES = '''
- hosts: localhost
  gather_facts: false
  tasks:
    - name: Manage Velocloud Gateways
      no_log: false
      gateway:
        host: "172.18.7.200"
        user: "super@velocloud.net"
        password: "vcadm!n"
        gateway_name: "{{ item.name }}"
        description: "{{ item }}"
        ip_address: "{{ item.ip }}"
        state: present
      with_items:
        - { name: 'test-ansible', ip: '1.1.1.1' }
        - { name: 'test-ansible2', ip: '2.2.2.2' }
      register: gateways
      tag: gateways
'''

from ansible.module_utils.basic import *
from uuid import uuid4

import velocloud
from velocloud.rest import ApiException
import urllib3


def create_gateway(host, user, password, name, description, ip_address):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl = False
    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = None
    result = {"id": 0,
              "activationKey": 0}

    UNIQ = str(uuid4())
    params = {"name": name,
              "networkId": 1,
              "gatewayPoolId": 1,
              "description": description,
              "ipAddress": ip_address}
    try:
        res = api.gatewayGatewayProvision(params)
        result["id"] = res.id
        result["activationKey"] = res.activationKey
        return result
    except:
        module.exit_json(changed=False, result="Gateway was not created")


def get_gateway(host, user, password, gateway_name):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl=False

    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = None
    gateway = None
    result = {"id": 0,
              "activationKey": 0}

    try:
        res = api.networkGetNetworkGateways({"networkId": 1})
        for gateway in res:
            if gateway.name == gateway_name:
                result["id"] = gateway.id
                result["activationKey"] = gateway.activationKey
                return result
        return None
    except:
        return None


def delete_gateway(host, user, password, id):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl=False

    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = None

    try:
        res = api.gatewayDeleteGateway({ "id": id })
        return res.id
    except:
        return None


def main():
    fields = {
        "host": {"required": True, "type": "str"},
        "user": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "gateway_name": {"required": True, "type": "str"},
        "description": {"required": False, "type": "str"},
        "ip_address": {"required": True, "type": "str"},
        "state": dict(default='present', choices=['present', 'absent'])
    }
    module = AnsibleModule(argument_spec=fields)

    host = module.params['host']
    user = module.params['user']
    password = module.params['password']
    description = module.params['description']
    ip_address = module.params['ip_address']
    gateway_name = module.params['gateway_name']

    gateway = get_gateway(host, user, password, gateway_name)
    if not gateway:
        # Gateway doesn't exist with this name, let's create it
        if module.params['state'] == 'present':
            create_result = create_gateway(host, user, password, gateway_name, description, ip_address)
            module.exit_json(changed=True, argument_spec=module.params, gateway_id=create_result["id"])
        else:
            module.exit_json(changed=False, argument_spec=module.params)

    if module.params['state'] == 'absent':
        # Delete Gateway
        delete_gateway(host, user, password, gateway["id"])
        module.exit_json(changed=True, argument_spec=module.params, gateway_id=gateway["id"])
    else:
        # Just return ID
        module.exit_json(changed=False, argument_spec=module.params, meta=gateway)

if __name__ == '__main__':
    main()

