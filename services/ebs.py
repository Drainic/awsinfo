import boto3
import logging
from settings import NO_VALUE, LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

def get_ebs_info(aws_session, show_unused=False):
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
