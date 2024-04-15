import logging

import parsers
import tools
from settings import LOGGER_NAME, NO_VALUE

logger = logging.getLogger(LOGGER_NAME)
args = parsers.programm_args
aws_session = tools.init_connection(profile_name=args.profile)

@tools.show_as_table
def get_ebs_info(show_unused=False):
    """Collect information about AWS volumes

    Args:
        show_unused (bool, optional): If True, the func will return only volumes
        with state=available. Defaults to False.

    Returns:
        ebs_data_list (list): List of hashes with EBS description
    """
    client = aws_session.client("ec2")
    paginator = client.get_paginator('describe_volumes')
    ebs_data_list = []
    filters = []
    if show_unused:
        filters.append(
            {
                'Name': "status",
                "Values":['available']
            }
        )
    for page in paginator.paginate(Filters=filters):
        for item in page['Volumes']:
            ebs = dict()
            ebs['VolumeId'] = item['VolumeId']
            ebs['Size(GB)'] = item['Size']
            ebs['Type'] = item['VolumeType']
            ebs['Created'] = item['CreateTime']
            ebs['AZ'] = item['AvailabilityZone']
            ebs['State'] = item['State']

            if 'Tags' in item:
                for tag in item['Tags']:
                    if tag['Key'] == "Name":
                        ebs['Name'] = tag['Value']
                        break
                    else:
                        ebs['Name'] = NO_VALUE
            else:
                ebs['Name'] = NO_VALUE
            ebs_data_list.append(ebs)
    if len(ebs_data_list) == 0:
        logger.info("No EBS were found")
    return ebs_data_list
