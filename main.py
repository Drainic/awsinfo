import logging.config

import boto3

from services.ebs import get_ebs_info
from parsers import create_parser
from services.s3 import S3
from settings import LOGGER_CONFIG, LOGGER_NAME
import tools

logging.config.dictConfig(LOGGER_CONFIG)
logger = logging.getLogger(LOGGER_NAME)

parser = create_parser()
args = parser.parse_args()

aws_session = tools.init_connection(profile_name=args.profile)

if args.service == 's3':
    logger.info("Analysing S3...")
    s3 = aws_session.client('s3')
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    data = []

    for bucket_name in buckets:
        s3_info = S3(
            bucket_name,
            aws_session=aws_session,
            last_modified=args.modified,
            encryption=args.encryption,
            public=args.public
        )
        data.append(s3_info.bucket_stat)
elif args.service == 'ebs':
    logger.info("Analysing EBS volumes...")
    data = get_ebs_info(aws_session=aws_session, show_unused=args.unused)

tools.show_as_table(data)
if args.csv:
    tools.store_as_csv(data=data)
exit()
