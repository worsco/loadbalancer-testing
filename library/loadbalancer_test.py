#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: loadbalancer_test

short_description: Test connectivity through Load Balancer

version_added: "2.6"

description:
    - "Testing connectivity through a Load Balancer to HTTP and HTTPS hosts"

options:
    host_list:
        description:
            - A list of hosts to test for from the LB
        required: true
    load_balancer_url:
        description:
            - A complete URL to access the load balancer for testing
        required: true
    test_timeout:
        description:
            - Total number of seconds to execute the test, defaults to 30
        required: false
    test_delay:
        description:
            - Number of seconds between each test, defaults to 0
        required: false

author:
    - Scott Worthington (scott.c.worthington@gmail.com)
'''

EXAMPLES = '''
# Test OpenShift hosts
- name: Test OpenShift hosts
  loadbalancer_test:
    host_list: "{{ ansible_play_hosts_all }}"
    load_balancer_url: "https://my_lb_name.domain.tld/"
# Pass in a message
- name: Test OpenShift hosts
  loadbalancer_testt:
    host_list:
      - hostone.domain.tld
      - hosttwo.domain.tld
      - hostthree.domain.tld
    load_balancer_url: "https://my_lb_name.domain.tld/"
    test_timeout: 30
    test_delay: 1
'''

RETURN = '''
hosts_seen:
    description: host name seen and the number of times seen
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url
import time
from datetime import datetime

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        host_list=dict(type='list', required=True),
        load_balancer_url=dict(type='str', required=True),
        test_timeout=dict(type='int', required=False, default=30),
        test_delay=dict(type='int', required=False, default=0)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        hosts_seen='',
        junk_output=''
    )


    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    #result['original_message'] = module.params['name']
    #result['message'] = 'goodbye'

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    #if module.params['new']:
    #    result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    #if module.params['name'] == 'fail me':
    #    module.fail_json(msg='You requested this to fail', **result)

    items_in_list = len(module.params['host_list'])

    start_time = datetime.now()
    now = datetime.now()
    duration = now - start_time

    hosts_seen={}
    junk_output={}

    while (duration.seconds <= module.params['test_timeout']) and (items_in_list != len(hosts_seen)):
        response = open_url(module.params['load_balancer_url'], method='GET', validate_certs=False)

        if response is not None:
            body = response.read()
            body = body.rstrip()
            # should we test to see if body is not in module.params['host_list'] then
            # don't add the output to hosts_seen

            if body in module.params['host_list']:
                if not body in hosts_seen:
                    hosts_seen.setdefault(body, 1)
                else:
                    hosts_seen[body] += 1
            else:
                if not body in junk_output:
                    junk_output.setdefault(body, 1)
                else:
                    junk_output[body] += 1 

        now = datetime.now()
        duration = now - start_time
        if (duration.seconds >= module.params['test_timeout']) or (len(hosts_seen) >= items_in_list):
            break
        time.sleep(module.params['test_delay'])

    for someitem in module.params['host_list']:
        if not someitem in hosts_seen:
            hosts_seen.setdefault(someitem, 0)

    result['hosts_seen'] = hosts_seen
    result['junk_output'] = junk_output

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
