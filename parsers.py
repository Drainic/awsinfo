import argparse


def create_parser():
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

    subparsers = parser.add_subparsers(dest="service")
    # Command: s3
    parser_s3 = subparsers.add_parser(
        "s3",
        help="get a list of S3 bucket from account",
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
        dest="public",
        help="Check public permissions for the S3 bucket",
    )
    return parser
