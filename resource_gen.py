import logging

from scotty import utils
from iperfserverclient.resource import IPerfResource

logger = logging.getLogger(__name__)

iPerfResource = None

def deploy(context):
    logger.info('Deploy iperf with heat')
    global iPerfResource
    iPerfResource = IPerfResource(context)
    iPerfResource.deploy(context)
    return iPerfResource.endpoint

def clean(context):
    iPerfResource.clean(context)
