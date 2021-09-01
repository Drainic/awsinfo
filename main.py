import logging.config

import tools
from parsers import create_parser
from services.ebs import get_ebs_info
from services.kms import get_kms_info
from services.s3 import get_s3_info
from services.lb import get_lb_info
from settings import LOGGER_CONFIG, LOGGER_NAME

logging.config.dictConfig(LOGGER_CONFIG)
logger = logging.getLogger(LOGGER_NAME)

parser = create_parser()
args = parser.parse_args()

aws_session = tools.init_connection(profile_name=args.profile)

if args.service == 's3':
    logger.info("Analysing S3...")
    data = get_s3_info(
        aws_session=aws_session,
        last_modified=args.modified,
        encryption=args.encryption,
        public=args.public
    )
elif args.service == 'ebs':
    logger.info("Analysing EBS volumes...")
    data = get_ebs_info(aws_session=aws_session, show_unused=args.unused)
elif args.service == 'kms':
    logger.info("Analysing KMS keys...")
    data = get_kms_info(aws_session=aws_session)
elif args.service == 'lb':
    logger.info("Analysing LBs...")
    data = get_lb_info(aws_session=aws_session, public=args.public)

tools.show_as_table(data)
if args.csv:
    tools.store_as_csv(data=data)
exit()
