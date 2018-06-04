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
module: edge
short_description: Manage your Velocloud Edge
'''


EXAMPLES = '''
    - name: Manage Velocloud Edges
      no_log: false
      edge:
        host: "172.16.65.168"
        user: "super@velocloud.net"
        password: "vcadm!n"
        edge_name: "{{ item.name }}"
        description: "{{ item.name }}"
        enterpriseId: "{{ enterprise.entreprise_id }}"
        configurationId: 20
        state: present
      with_items:
        - { name: 'test-ansible1' }
        - { name: 'test-ansible2' }
        - { name: 'test-ansible3' }
        - { name: 'test-ansible4' }
        - { name: 'test-ansible5' }
      register: edge
      tag: edges
'''

from ansible.module_utils.basic import *
from uuid import uuid4

import velocloud
from velocloud.rest import ApiException
import urllib3


def create_edge(host, user, password, name, description, model_number, enterprise_id, configuration_id):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl = False
    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = None
    result = {"id": 0,
              "activationKey": 0}

    params = {"name": name,
              "description": description,
              "modelNumber": model_number,
              "enterpriseId": enterprise_id,
              "configurationId": configuration_id}
    try:
        res = api.edgeEdgeProvision(params)
        result["id"] = res.id
        result["activationKey"] = res.activationKey
        return result
    except Exception as e:
        module.exit_json(changed=False, result="Edge was not created")


def get_edge(host, user, password, edge_name, enterprise_id):
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
        res = api.enterpriseGetEnterpriseEdges({"enterpriseId": enterprise_id})
        for edge in res:
            if edge.name == edge_name:
                result["id"] = edge.id
                result["activationKey"] = edge.activationKey
                return result
        return None
    except Exception as e:
        return None


def delete_edge(host, user, password, id, enterprise_id):
    urllib3.disable_warnings()
    velocloud.configuration.verify_ssl=False

    client = velocloud.ApiClient(host=host)
    client.authenticate(user, password, operator=True)
    api = velocloud.AllApi(client)
    res = None

    params = {"id": id,"enterpriseId": enterprise_id}

    try:
        res = api.edgeDeleteEdge(params)
        return res.id
    except:
        return None


def main():
    fields = {
        "host": {"required": True, "type": "str"},
        "user": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "edge_name": {"required": True, "type": "str"},
        "description": {"required": False, "type": "str"},
        "modelNumber": {"required": False, "type": "str", "default": "virtual"},
        "enterpriseId": {"required": True, "type": "int"},
        "configurationId": {"required": False, "type": "int"},
        "state": dict(default='present', choices=['present', 'absent'])
    }
    module = AnsibleModule(argument_spec=fields)

    host = module.params['host']
    user = module.params['user']
    password = module.params['password']
    description = module.params['description']
    model_number = module.params['modelNumber']
    enterprise_id = module.params['enterpriseId']
    configuration_id = module.params['configurationId']
    edge_name = module.params['edge_name']

    edge = get_edge(host, user, password, edge_name, enterprise_id)
    if not edge:
        # Edge doesn't exist with this name, let's create it
        if module.params['state'] == 'present':
            create_result = create_edge(host, user, password, edge_name, description, model_number, enterprise_id, configuration_id)
            module.exit_json(changed=True, argument_spec=module.params, edge_id=create_result["id"])
        else:
            module.exit_json(changed=False, argument_spec=module.params)

    if module.params['state'] == 'absent':
        # Delete Edge
        delete_edge(host, user, password, edge["id"], enterprise_id)
        module.exit_json(changed=True, argument_spec=module.params, edge_id=edge["id"])
    else:
        # Just return ID
        module.exit_json(changed=False, argument_spec=module.params, meta=edge)

if __name__ == '__main__':
    main()

