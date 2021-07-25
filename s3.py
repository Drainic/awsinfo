from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
import logging.config
from settings import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('aws_info_logger')

class S3:
    def __init__(self, name, last_modified=False, encryption=False) -> None:
        self.name = name
        self.size = 0
        self.object_number = 0
        self.last_modified = last_modified
        self.public = False
        self.encryption = encryption
        self.client_s3 = boto3.client('s3')
        self.client_cw = boto3.client('cloudwatch')
        self._get_bucket_size()
        self._get_object_number()

    @property
    def bucket_stat(self,acl=False) -> dict:
        common_info = {
            "Bucket_name": self.name,
            "Size(MB)": self.size,
            "ObjectNum": self.object_number
        }
        if self.last_modified:
            common_info['Last_modified'] = self._get_last_modified_date()
        if self.encryption:
            common_info['Encrypted'], common_info['Encrypt_type'] = self._check_encryption()
        if acl:
            common_info['ACL']
        return common_info

    def _get_last_modified_date(self) -> str:
        # Get last modified file(do not analyse if number of objects is more than OBJECT_NUMBER)
        if self.object_number > 70000:
            self.last_modified = "NotAnalysed"
        elif self.object_number == 0:
            self.last_modified = ""
        else:
            try:
                get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))
                paginator = self.client_s3.get_paginator( "list_objects_v2" )
                page_iterator = paginator.paginate( Bucket = self.name)
                for page in page_iterator:
                    if "Contents" in page:
                        result = [obj['LastModified'] for obj in sorted( page["Contents"], key=get_last_modified)][-1]
                        return result.strftime("%d-%m-%Y %H:%M:%S")
            except ClientError as e:
                logger.error(e)
                return "NoPermission"

    def _check_encryption(self):
        try:
            enc = self.client_s3.get_bucket_encryption(Bucket=self.name)
            rules = enc['ServerSideEncryptionConfiguration']['Rules'][0]['ApplyServerSideEncryptionByDefault']
            #print('Bucket: %s, Encryption: %s' % (self.name, rules))
            if rules['SSEAlgorithm'] ==  'AES256':
                return True, "SSE-S3"
            elif rules['SSEAlgorithm'] == 'aws:kms':
                return True, "SSE-KMS"
        except ClientError as e:
            # In case if there is no encryption in place
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                return False, "None"
            else:
                logger.error(f"Bucket: {self.name}, unexpected error: {e}")
                return "Error", "Error"

    def _get_bucket_size(self):
        try:
            response = self.client_cw.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': self.name},
                    {'Name': 'StorageType', 'Value': 'StandardStorage'}
                ],
                Statistics=['Average'],
                Period=3600,
                StartTime=datetime.now() - timedelta(days=2),
                EndTime=datetime.now(),
                Unit='Bytes'
            )
            if len(response["Datapoints"]) > 0:
                self.size = round(int(response["Datapoints"][0]["Average"])/1024/1024, 2)
            else:
                self.size = "Empty"
        except ClientError as e:
            logger.error(e)
            self.size = "NoPermissions"

    def _get_object_number(self) -> int:
        try:
            response = self.client_cw.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='NumberOfObjects',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': self.name},
                    {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
                ],
                Statistics=['Average'],
                Period=3600,
                StartTime=datetime.now() - timedelta(days=2),
                EndTime=datetime.now(),
                Unit='Count'
            )
            if len(response["Datapoints"]) > 0:
                self.object_number = int(response["Datapoints"][0]["Average"])
            else:
                self.object_number = 0
        except ClientError as e:
            logger.error(e)
            self.size = "NoPermissions"
