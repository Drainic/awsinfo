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
    parser = argparse.ArgumentParser()
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

    # Command: s3
    parser_s3 = subparsers.add_parser(
        "s3",
        help="get a list of S3 bucket from the current AWS account",
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

    # Command: EBS
    parser_ebs = subparsers.add_parser(
        "ebs",
        help="get a list of EBS in the current AWS account",
    )
    parser_ebs.add_argument(
        "-u", "--unused",
        action="store_true",
        required=False,
        help="Show only unused EVS volumes",
    )
    return parser
