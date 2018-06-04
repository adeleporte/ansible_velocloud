#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2015 VMware, Inc. All Rights Reserved.
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
# MODIFIED FROM YFAUSER VERSION


__author__ = 'adeleporte'


from pyVim import connect
from pyVmomi import vim
import requests
import ssl
import atexit


def find_virtual_machine(content, searched_vm_name):
    virtual_machines = get_all_objs(content, [vim.VirtualMachine])
    for vm in virtual_machines:
        if vm.name == searched_vm_name:
            return vm
    return None


def get_all_objs(content, vimtype):
    obj = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for managed_object_ref in container.view:
        obj.update({managed_object_ref: managed_object_ref.name})
    return obj


def connect_to_api(vchost, vc_user, vc_pwd):
    if hasattr(ssl, 'SSLContext'):
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
    else:
        context = None
    if context:
        service_instance = connect.SmartConnect(host=vchost, user=vc_user, pwd=vc_pwd, sslContext=context)
    else:
        service_instance = connect.SmartConnect(host=vchost, user=vc_user, pwd=vc_pwd)

    atexit.register(connect.Disconnect, service_instance)

    return service_instance.RetrieveContent()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            ovftool_path=dict(required=True, type='str'),
            ova_file=dict(required=True, type='str'),
            vcenter=dict(required=True, type='str'),
            vcenter_user=dict(required=True, type='str'),
            vcenter_passwd=dict(required=True, type='str', no_log=True),
            datacenter=dict(required=True, type='str'),
            cluster=dict(required=True, type='str'),
            disk_mode=dict(required=False, type='str', default='thin'),
            datastore=dict(required=True, type='str'),
            portgroup=dict(required=True, type='str'),
            vmname=dict(required=True, type='str'),
            instanceid=dict(required=True, type='str'),
            hostname=dict(required=True, type='str'),
            password=dict(required=True, type='str'),
            publickeys=dict(required=False, type='str'),
            dns1=dict(required=False, type='str', default='8.8.8.8'),
            dns2=dict(required=False, type='str', default='8.8.4.4'),
            eth0ipAllocationType=dict(required=False, type='str', default='DHCP'),
            eth0ipAddress=dict(required=False, type='str'),
            eth0subnetMask=dict(required=False, type='str'),
            eth0gatewayAddress=dict(required=False, type='str'),
            userdata=dict(required=False, type='str')
        ),
        supports_check_mode=True
    )

    try:
        content = connect_to_api(module.params['vcenter'], module.params['vcenter_user'],
                                 module.params['vcenter_passwd'])
    except vim.fault.InvalidLogin:
        module.fail_json(msg='exception while connecting to vCenter, login failure, check username and password')
    except requests.exceptions.ConnectionError:
        module.fail_json(msg='exception while connecting to vCenter, check hostname, FQDN or IP')

    vrli_appliance_vm = find_virtual_machine(content, module.params['vmname'])

    if vrli_appliance_vm:
        #module.fail_json(msg='A VM with the name {} was already present')
        module.exit_json(changed=False, vrli_appliance_vm=str(vrli_appliance_vm))

    if module.check_mode:
        module.exit_json(changed=True)

    ovftool_exec = '{}/ovftool'.format(module.params['ovftool_path'])
    ova_file = '{}'.format(module.params['ova_file'])
    vi_string = 'vi://{}:{}@{}/{}/host/{}/'.format(module.params['vcenter_user'],
                                                   module.params['vcenter_passwd'], module.params['vcenter'],
                                                   module.params['datacenter'], module.params['cluster'])

    ova_tool_result = module.run_command([ovftool_exec, '--acceptAllEulas', '--skipManifestCheck',
                                          '--powerOn', '--noSSLVerify', '--allowExtraConfig',
                                          '--diskMode={}'.format(module.params['disk_mode']),
                                          '--datastore={}'.format(module.params['datastore']),
                                          '--network={}'.format(module.params['portgroup']),
                                          '--name={}'.format(module.params['vmname']),
                                          '--prop:instance-id={}'.format(module.params['instanceid']),
                                          '--prop:hostname={}'.format(module.params['hostname']),
                                          '--prop:password={}'.format(module.params['password']),
                                          '--prop:public-keys={}'.format(module.params['publickeys']),
                                          '--prop:dns1={}'.format(module.params['dns1']),
                                          '--prop:dns2={}'.format(module.params['dns2']),
                                          '--prop:eth0.ipAllocationType={}'.format(module.params['eth0ipAllocationType']),
                                          '--prop:eth0.ipAddress={}'.format(module.params['eth0ipAddress']),
                                          '--prop:eth0.subnetMask={}'.format(module.params['eth0subnetMask']),
                                          '--prop:eth0.gatewayAddress={}'.format(module.params['eth0gatewayAddress']),
                                          '--prop:user-data={}'.format(module.params['userdata']),
                                          ova_file, vi_string])

    if ova_tool_result[0] != 0:
        module.fail_json(msg='Failed to deploy OVA, error message from ovftool is: {}'.format(ova_tool_result[1]))

    module.exit_json(changed=True, ova_tool_result=ova_tool_result)

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
