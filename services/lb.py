import logging

from settings import LOGGER_NAME, NO_VALUE

LOGGER = logging.getLogger(LOGGER_NAME)

def get_lb_info(aws_session, public=False):
    """Get the list of load balancers from the AWS account

    Args:
        aws_session : Internal AWS session
        public (bool, optional): Show only public loadbalancers. Defaults to False.

    Returns:
        [type]: [description]
    """
    # Get ELB list
    lb_list = []
    client = aws_session.client('elbv2')
    paginator = client.get_paginator('describe_load_balancers')
    for page in paginator.paginate():
        for lb in page['LoadBalancers']:
            lb_info = dict()
            if public and lb['Scheme'] == 'internal':
                continue
            lb_info['LB_name'] = lb['LoadBalancerName']
            lb_info['Schema'] = lb['Scheme']
            lb_info['State'] = lb['State']['Code']
            lb_info['Type'] = lb['Type']
            lb_info['VPC_ID'] = lb['VpcId']
            lb_info['DNS_zone'] = lb['CanonicalHostedZoneId']
            lb_info['DNS_name'] = lb['DNSName']
            lb_list.append(lb_info)

    # Get clasic LB list
    client = aws_session.client('elb')
    paginator = client.get_paginator('describe_load_balancers')
    for page in paginator.paginate():
        for lb in page['LoadBalancerDescriptions']:
            lb_info = dict()
            if public and lb['Scheme'] == 'internal':
                continue
            lb_info['LB_name'] = lb['LoadBalancerName']
            lb_info['Schema'] = lb['Scheme']
            lb_info['State'] = NO_VALUE
            lb_info['Type'] = 'classic'
            lb_info['VPC_ID'] = lb['VPCId']
            lb_info['DNS_zone'] = lb['CanonicalHostedZoneNameID']
            lb_info['DNS_name'] = lb['DNSName']
            lb_list.append(lb_info)

    if len(lb_list) == 0:
        LOGGER.info('No ELB found')

    return lb_list
