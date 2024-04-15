"""Support stuff for main.py
"""
import concurrent.futures
import csv
import functools
import logging
from typing import NoReturn

import boto3
from botocore.exceptions import ClientError, ProfileNotFound
from tabulate import tabulate
from tqdm import tqdm

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
        exit(1)


def store_as_csv(data: list) -> NoReturn:
    """Takes the list of dicts and save is as a CSV file (result.csv) in the same folder

    Args:
        data (List[Dict]): Should be a list of dictionares. Dicts keays are used as column names
    """
    if len(data) > 0:
        with open('result.csv', 'w', newline='') as output_file:
            data_writer = csv.DictWriter(output_file, fieldnames=data[0].keys())
            data_writer.writeheader()
            data_writer.writerows(data)
            logger.info("The file %s was created", output_file.name)


def run_thread(f, my_iter, *args, **kwargs):
    with tqdm(total=len(my_iter), desc="Progress", colour='green', ncols=100) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(f, arg, *args, **kwargs): arg for arg in my_iter}
            results = []
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
                pbar.update(1)
    return results


# Decorators
def add_footer(func):
    @functools.wraps(func)
    def wrapper_function(*args, **kwargs):
        results = func(*args, **kwargs)
        if results is not None:
            print(f"Total findings: {len(results)}")
        return results
    return wrapper_function


def show_as_table(func):
    """The decorator takes a function which returns list of string or dicts
    and show it in console as a table"""
    @functools.wraps(func)
    @add_footer
    def wrapper_table(*args, **kwargs):
        result = func(*args, **kwargs)
        if len(result) == 0:
            return None
        if type(result[0]) == str:
            for index, item in enumerate(result):
                print(f"{index:^4} -> {item:.^20}")
        elif type(result[0]) == dict:
            headers = result[0].keys()
            rows = [i.values() for i in result]
            print(tabulate(rows, headers=headers, showindex=False, tablefmt="presto", numalign="right"))
        return result
    return wrapper_table
