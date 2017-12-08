import logging
import string
import random
import os
from time import sleep

import keystoneauth1.loading
import keystoneauth1.session
import heatclient.client
import novaclient.client
from heatclient.common import template_utils

logger = logging.getLogger(__name__)


class IPerfResource(object):
    def __init__(self, context):
        self.reduce_logging()
        resource = context.v1.resource
        self.heat_stack_name = resource.name
        keystone_password_loader = keystoneauth1.loading.get_plugin_loader('password')
        auth = keystone_password_loader.load_from_options(
            auth_url = resource.params['auth_url'],
            username = resource.params['username'],
            password = resource.params['password'],
            project_name = resource.params['project_name']
        )
        keystone_session = keystoneauth1.session.Session(auth=auth)
        self._heat = heatclient.client.Client('1', session=keystone_session)
        self._nova = novaclient.client.Client('2', session=keystone_session)
        self.endpoint = {}
        self.template_path = self.get_template_path()

    def reduce_logging(self):
        reduce_loggers = {
                'keystoneauth.identity.v2',
                'keystoneauth.identity.v2.base',
                'keystoneauth.session',
                'urllib3.connectionpool',
                'stevedore.extension'}
        for logger in reduce_loggers:
            logging.getLogger(logger).setLevel(logging.WARNING)

    def get_template_path(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(script_dir, '../templates/iperf-server-client-stack.yaml')
        template_path = os.path.normpath(template_path)
        return template_path

    def deploy(self, context):
        # During Development delete old stack
        try:
            self._delete_stack()
        except:
            pass
        logger.info('Start to create stack ({})'.format(self.heat_stack_name))
        self.create_password()
        heat_stack_args = self._create_heat_stack_args(self.scotty_password)
        self._heat.stacks.create(**heat_stack_args)
        stack = self._wait_for_stack_complete()
        self.endpoint = self._get_endpoint(stack)
        logger.info('endpoint: {}'.format(self.endpoint))

    def create_password(self):
        chars = string.ascii_uppercase + string.digits
        size = 8
        self.scotty_password = ''.join(random.SystemRandom().choice(chars) for _ in range(size))

    def _create_heat_stack_args(self, scotty_password):
        tpl_files, template = template_utils.get_template_contents(self.template_path)
        args = {
           'stack_name':self.heat_stack_name,
           'template':template,
           'files': tpl_files,
           'parameters': {
             'public_net_id': 'public',
             'private_net_id': 'private-1a03e53738ad4854b9610273945c2b6b',
             'private_subnet_id': '30e4947e-6479-419c-8f85-a20c993bb939',
             'scotty_password': scotty_password
           },
        }
        return args

    def _wait_for_stack_complete(self):
        while True:
           sleep(5)
           stack = self._heat.stacks.get(self.heat_stack_name)
           status = stack.stack_status
           if status == 'CREATE_COMPLETE':
               return stack
           if status == 'CREATE_FAILED':
               raise Exception('Stack create failed')

    def _get_endpoint(self, stack):
        endpoint = {
          'iperf-server': {
            'ip': None,
            'user': 'scotty',
            'password': self.scotty_password
          },
          'iperf-client': {
            'ip': None,
            'user': 'scotty',
            'password': self.scotty_password
          }
        }
        for output in stack.to_dict().get('outputs', []):
          if output['output_key'] == 'iperf-client_public_ip':
            endpoint['iperf-client']['ip'] =  output['output_value'][0]
          elif output['output_key'] == 'iperf-server_private_ip':
            endpoint['iperf-server']['ip'] =  output['output_value'][0]
        return endpoint

    def clean(self, context):
        logger.warning('Skip clean resources for iperf-server-client')
        return
        self._delete_stack()

    def _delete_stack(self):
        self._heat.stacks.delete(self.heat_stack_name)
        self._wait_for_stack_deleted()

    def _wait_for_stack_deleted(self):
        logger.info("wait for stack ({}) delete".format(self.heat_stack_name))
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
