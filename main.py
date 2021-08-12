import csv
import logging.config

import boto3
from botocore.exceptions import ClientError, ProfileNotFound
from tabulate import tabulate

from parsers import create_parser
from s3 import S3
from settings import LOGGER_CONFIG

logging.config.dictConfig(LOGGER_CONFIG)
logger = logging.getLogger('aws_info_logger')

parser = create_parser()
args = parser.parse_args()

#### Set profile. Check region
try:
    session = boto3.session.Session(profile_name=args.profile)
    account_id = session.client("sts").get_caller_identity()["Account"]
except (ClientError, ProfileNotFound) as e:
    logger.error(e)
    exit()

paginator = session.client('iam').get_paginator('list_account_aliases')
for response in paginator.paginate():
    account_name = response['AccountAliases'][0]
logger.info(f"Profile: {args.profile}, Region: {session.region_name}, Account_name: {account_name}, Accounf ID: {account_id}")

def show_as_table(data):
    if len(data) > 0:
        header = data[0].keys()
        rows = [i.values() for i in data]
        print(tabulate(rows, header))
        print("Total findings: {}\n".format(len(data)))

def store_as_csv(data):
    if len(data) > 0:
        with open('result.csv', 'w', newline='') as output_file:
            data_writer = csv.DictWriter(output_file, fieldnames=data[0].keys())
            data_writer.writeheader()
            data_writer.writerows(data)
            logger.info("The file %s was created", output_file.name)

if args.service == 's3':
    logger.info("Analysing S3")
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    bucket_info = []

    for bucket_name in buckets:
        s3_info = S3(
            bucket_name,
            last_modified=args.modified,
            encryption=args.encryption,
            public=args.public
        )
        bucket_info.append(s3_info.bucket_stat)

    show_as_table(data=bucket_info)
    if args.csv:
        store_as_csv(data=bucket_info)
    exit()
