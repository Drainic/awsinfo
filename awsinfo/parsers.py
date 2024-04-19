"""Setting for argument parsing
The module contains everything related to argument
parsing
"""
import argparse


def create_parser():
    """Create parser object

    Returns:
        parser: Python object with parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog="awsinfo",
        description="Get info from AWS account and shows it as a table"
    )
    parser.add_argument(
        '-p', '--profile',
        default='default',
        required=False,
        metavar="AWS_PROFILE_NAME",
        help='Which AWS profile from config file will be used'
    )
    parser.add_argument(
        '--csv',
        action="store_true",
        required=False,
        help="Additionaly saves result into the file in the current dir",
    )
    subparsers = parser.add_subparsers(
        dest="service",
        metavar="SERVICE_NAME",
        required=True,
        help="The service name for getting information"
    )

    # Service: s3
    parser_s3 = subparsers.add_parser(
        "s3",
        help="Show all S3 bucket from the current AWS account",
    )
    parser_s3.add_argument(
        "-m", "--modified",
        action="store_true",
        required=False,
        help="Get the date when S3 bucket was modified last time (Can take additional time)",
    )
    parser_s3.add_argument(
        "-e", "--encryption",
        action="store_true",
        required=False,
        help="Collect info about encryption for S3 buckets",
    )
    parser_s3.add_argument(
        "-p", "--public",
        action="store_true",
        required=False,
        help="Check public permissions for the S3 bucket",
    )

    # Service: EBS
    parser_ebs = subparsers.add_parser(
        "ebs",
        help="Show all EBS in the current AWS account",
    )
    parser_ebs.add_argument(
        "-u", "--unused",
        action="store_true",
        required=False,
        help="Show only unused EBS volumes",
    )

    # Service: KMS
    parser_kms = subparsers.add_parser(
        "kms",
        help="Show all KMS keys in the current AWS account",
    )

    # Service: Lambda
    parser_kms = subparsers.add_parser(
        "lambda",
        help="Show all Lambda functions in the current AWS account",
    )

    # Service: LB
    parser_lb = subparsers.add_parser(
        "lb",
        help="Show all Load balancers in the current AWS account",
    )
    parser_lb.add_argument(
        "-p", "--public",
        action="store_true",
        required=False,
        help="Show only public LBs",
    )

    parser_lb = subparsers.add_parser(
        "glue",
        help="Show all Glue DBs and it's tables in the current AWS account",
    )
    return parser


parser = create_parser()
programm_args = parser.parse_args()
