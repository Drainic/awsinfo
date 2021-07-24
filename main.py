import argparse
import logging.config
import boto3
from tabulate import tabulate
from s3 import S3
from settings import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('aws_info_logger')

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="service")
# Command: s3
parser_s3 = subparsers.add_parser(
    "s3",
    help="get a list of S3 bucket from account",
)
parser_s3.add_argument(
    "-c", "--changed",
    action="store_true",
    required=False,
    help="Show the date when S3 bucket was modified (Can take additional time)",
)
parser_s3.add_argument(
    "-e", "--encryption",
    action="store_true",
    required=False,
    help="Show if encryption enabled and encryption time",
)

#### Set profile. Check region
aws_profile = 'default'
working_session = boto3.session.Session(profile_name=aws_profile)
logger.info(f"Profile: {aws_profile}, region: {working_session.region_name}")

args = parser.parse_args()
if args.service == 's3':
    logger.info("Analysing S3")
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    bucket_info = []

    for bucket_name in buckets:
        s3_info = S3(bucket_name, last_modified=args.changed, encryption=args.encryption)
        bucket_info.append(s3_info.bucket_stat)

    def show_as_table(table_name,data):
        if len(data) > 0:
            print(table_name)
            header = data[0].keys()
            rows   = [i.values() for i in data]
            print(tabulate(rows, header))
            print("Total findings: {}\n".format(len(data)))

    show_as_table(table_name = "S3 buckets",data = bucket_info)
    exit()

