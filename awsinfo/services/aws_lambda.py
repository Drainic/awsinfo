import boto3
import tools
from typing import NoReturn, List, Dict
from datetime import datetime, timedelta

def list_lambdas() -> List[Dict]:
    functions = []
    lambda_client = boto3.client('lambda')
    paginator = lambda_client.get_paginator('list_functions')

    for page in paginator.paginate():
        for function in page['Functions']:
            functions.append(function)

    return functions

# TODO: add parameters instead of using 6 month

def get_lambda_info(function) -> Dict:
    cloudwatch = boto3.client('cloudwatch')
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/Lambda',
        MetricName='Invocations',
        Dimensions=[
            {
            'Name': 'FunctionName',
            'Value': function['FunctionName']
            },
        ],
        StartTime=datetime.now() - timedelta(days=180),
        EndTime=datetime.now(),
        Period=15638400,  # seconds in a 6 months
        Statistics=['Sum']
    )

    if len(response['Datapoints']) == 0:
        usage_status = "Not used"
    else:
        usage_status = "In-use"
    return {
        'Function_name': function['FunctionName'],
        'Runtime': function.get('Runtime', "None"),
        'MemorySize': function.get('MemorySize', "None"),
        'LastModified': function.get('LastModified', "None"),
        'UsageStatus': usage_status
    }


@tools.show_as_table
def get_info():
    functions = list_lambdas()
    return tools.run_thread(get_lambda_info, functions)


