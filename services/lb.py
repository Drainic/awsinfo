# List LB's (Name state Type DNS name)
# filter for public LB's

import logging
from settings import NO_VALUE, LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

def get_lb_info(aws_session, public=False):
    # Get ELB list
    elb_list = []
    client = aws_session.client('elbv2')
    paginator = client.get_paginator('describe_load_balancers')
    for page in paginator.paginate():
        for lb in page['LoadBalancers']:
            lb_info = dict()
            lb_info['LB_name'] = lb['LoadBalancerName']
            lb_info['Schema'] = lb['Scheme']
            lb_info['State'] = lb['State']['Code']
            lb_info['Type'] = lb['Type']
            lb_info['VPC_ID'] = lb['VpcId']
            lb_info['DNS_zone'] = lb['CanonicalHostedZoneId']
            lb_info['DNS_name'] = lb['DNSName']
            elb_list.append(lb_info)

    # Get clasic LB list
    client = aws_session.client('elb')
    paginator = client.get_paginator('describe_load_balancers')
    for page in paginator.paginate():
        for lb in page['LoadBalancerDescriptions']:
            lb_info = dict()
            lb_info['LB_name'] = lb['LoadBalancerName']
            lb_info['Schema'] = lb['Scheme']
            lb_info['State'] = NO_VALUE
            lb_info['Type'] = 'classic'
            lb_info['VPC_ID'] = lb['VPCId']
            lb_info['DNS_zone'] = lb['CanonicalHostedZoneNameID']
            lb_info['DNS_name'] = lb['DNSName']
            elb_list.append(lb_info)

    if len(elb_list) == 0:
        logger.info('No ELB found')

    return elb_list
