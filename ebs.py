from logging import Filter
import boto3
from settings import NO_VALUE

def get_ebs_info(show_unused=False):
    client = boto3.client("ec2")
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
                    else:
                        ebs['Name'] = NO_VALUE
            else:
                ebs['Name'] = NO_VALUE
            ebs_data_list.append(ebs)
    return ebs_data_list