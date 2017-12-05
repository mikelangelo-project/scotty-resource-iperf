import logging
import os
from time import sleep

import keystoneauth1.loading
import keystoneauth1.session
import heatclient.client

logger = logging.getLogger(__name__)


class IPerfResource(object):
    heat_stack_name = 'iperf-server-client'
    def __init__(self, context):
        resource = context.v1.resource
        keystone_password_loader = keystoneauth1.loading.get_plugin_loader('password')
        auth = keystone_password_loader.load_from_options(
            auth_url = resource.params['auth_url'],
            username = resource.params['username'],
            password = resource.params['password'],
            project_name = resource.params['project_name']
        )
        keystone_session = keystoneauth1.session.Session(auth=auth)
        self._heat = heatclient.client.Client('1', session=keystone_session)
        self.endpoint = {}

    def deploy(self, context):
        heat_stack_args = self._create_heat_stack_args()
        self._heat.stacks.create(**heat_stack_args)
        self._wait_for_stack_complete()
        self.endpoint = {
            'url': 'url',
            'user': 'user',
            'password': 'password'
        }

    def _create_heat_stack_args(self):
        template_content = self._load_template_content()
        args = {
           'stack_name':self.heat_stack_name,
           'template':template_content
        }
        return args

    def _wait_for_stack_complete(self):
        while True:
           sleep(5)
           stack = self._heat.stacks.get(self.heat_stack_name)
           status = stack.stack_status
           if status == 'CREATE_COMPLETE':
               return
           if status == 'CREATE_FAILED':
               raise Exception('Stack create failed')

    def _load_template_content(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(script_dir, '../templates/iperf-server-client-stack.yaml')
        template_path = os.path.normpath(template_path)
        with open(template_path, 'r') as template_file:
            template_content = template_file.read()
        return template_content

    def clean(self, context):
        self._heat.stacks.delete(self.heat_stack_name)
        self._wait_for_stack_deleted()

    def _wait_for_stack_deleted(self):
        while True:
            sleep(5)
            try:
                stack = self._heat.stacks.get(self.heat_stack_name)
                status = stack.stack_status
            except Exception:
                status = False
            if status == 'DELETE_COMPLETE' or not status:
                return 
            if status == 'DELETE_FAILED':
                raise Exception('Stack delete failed')
