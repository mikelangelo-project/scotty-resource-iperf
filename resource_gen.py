import logging

from scotty import utils
from iperfserverclient.resource import IPerfResource

logger = logging.getLogger(__name__)



def deploy(context):
    logger.info('Deploy iperf with heat')
    iPerfResource = IPerfResource(context)
    iPerfResource.deploy(context)
    return iPerfResource.endpoint

def clean(context):
    iPerfResource = IPerfResource(context)
    iPerfResource.clean(context)
