"""Support stuff for main.py
"""

import csv
import logging

import boto3
from botocore.exceptions import ClientError, ProfileNotFound
from tabulate import tabulate

from settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

def init_connection(profile_name):
    """Check connection with AWS account. Get parameters of the session and return AWS session

    Args:
        profile_name (str): AWS profile name which will be used for connection
    """
    try:
        session = boto3.session.Session(profile_name=profile_name)
        account_id = session.client("sts").get_caller_identity()["Account"]

        paginator = session.client('iam').get_paginator('list_account_aliases')
        for response in paginator.paginate():
            account_name = response['AccountAliases'][0]
        logger.info(f"Profile: {profile_name}, Region: {session.region_name}, Account_name: {account_name}, Account ID: {account_id}")
        return session
    except (ClientError, ProfileNotFound) as e:
        logger.error(e)
        exit()

def store_as_csv(data):
    if len(data) > 0:
        with open('result.csv', 'w', newline='') as output_file:
            data_writer = csv.DictWriter(output_file, fieldnames=data[0].keys())
            data_writer.writeheader()
            data_writer.writerows(data)
            logger.info("The file %s was created", output_file.name)

def show_as_table(data):
    """Show data in a table format

    Args:
        data (list): Should be a list of hashes. Keys of the first element will be used as column names
    """
    if len(data) > 0:
        header = data[0].keys()
        rows = [i.values() for i in data]
        print(tabulate(rows, header, showindex=False, tablefmt="presto", numalign="right"))
        print("Total findings: {}\n".format(len(data)))
