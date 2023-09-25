import concurrent.futures
import logging.config
from datetime import datetime, timedelta

import tools
import parsers
from botocore.exceptions import ClientError
from settings import LOGGER_NAME, NO_VALUE
from tqdm import tqdm

logger = logging.getLogger(LOGGER_NAME)
args = parsers.programm_args
aws_session = tools.init_connection(profile_name=args.profile)


def s3_info(bucket_name, last_modified, encryption, public):
    s3_info = S3(
        bucket_name,
        last_modified=last_modified,
        encryption=encryption,
        public=public
    )
    return s3_info.bucket_stat


def run(f, my_iter, last_modified, encryption, public):
    l = len(my_iter)
    with tqdm(total=l, desc="Progress", colour='green', ncols=100) as pbar:
        # let's give it some more threads:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(s3_info, arg, last_modified, encryption, public): arg for arg in my_iter}
            results = []
            for future in concurrent.futures.as_completed(futures):
                arg = futures[future]
                results.append(future.result())
                pbar.update(1)
    return results

@tools.show_as_table_dec
def get_s3_info(last_modified, encryption, public):
    s3 = aws_session.client('s3')
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]

    return run(s3_info, buckets, last_modified, encryption, public)


class S3:
    def __init__(self, name, last_modified=False, encryption=False, public=False) -> None:
        self.name = name
        self.size = 0
        self.object_number = 0
        self.last_modified = last_modified
        self.public = public
        self.encryption = encryption
        self.client_s3 = aws_session.client('s3')
        self.client_cw = aws_session.client('cloudwatch')

        # TODO: need to check how to get file number and size
        # self._get_bucket_size()
        # self._get_object_number()

    @property
    def bucket_stat(self) -> dict:
        common_info = {
            "Bucket_name": self.name,
            # "Size(MB)": self.size,
            # "ObjectNum": self.object_number
        }
        if self.last_modified:
            common_info['Last_modified'] = self._get_last_modified_date()
        if self.encryption:
            common_info['Encrypted'], common_info['Encrypt_type'] = self._check_encryption()
        if self.public:
            common_info['Public_permissions'] = self._get_bucket_acl()
        common_info['Versioning'] = self._check_versioning()
        return common_info

    def _get_last_modified_date(self) -> str:
        # Get last modified file(do not analyse if number of objects is more than OBJECT_NUMBER)
        if self.object_number > 70000:
            return("NotAnalysed")
        elif self.object_number == 0:
            return(NO_VALUE)
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
            if rules['SSEAlgorithm'] == 'AES256':
                return True, "SSE-S3"
            elif rules['SSEAlgorithm'] == 'aws:kms':
                return True, "SSE-KMS"
        except ClientError as e:
            # In case if there is no encryption in place
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                return False, NO_VALUE
            else:
                logger.error(f"Bucket: {self.name}, unexpected error: {e}")
                return "Error", "Error"

    def _check_versioning(self):
        try:
            response = self.client_s3.get_bucket_versioning(Bucket=self.name)
            return response.get('Status', 'Disabled')
        except ClientError as e:
            logger.error(f"Bucket: {self.name}, unexpected error: {e}")
            return "Error"

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
                self.size = NO_VALUE
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

    def _get_bucket_acl(self) -> list:
        public_acl_indicator = 'http://acs.amazonaws.com/groups/global/AllUsers'
        permissions_to_check = {'READ', 'WRITE', 'READ_ACP', 'WRITE_ACP', 'FULL_CONTROL'}
        current_permission = []
        try:
            bucket_acl_response = self.client_s3.get_bucket_acl(Bucket=self.name)
            for grant in bucket_acl_response['Grants']:
                for (k, v) in grant.items():
                    if k == 'Permission' and any(permission in v for permission in permissions_to_check):
                        for (grantee_attrib_k, _) in grant['Grantee'].items():
                            if 'URI' in grantee_attrib_k and grant['Grantee']['URI'] == public_acl_indicator:
                                current_permission.append(v)
            return current_permission
        except ClientError as e:
            logger.error(e)
