import boto3
from moto import mock_s3
import pytest

@mock_s3
def test_list_s3_buckets():
    # Create a mock S3 bucket
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='mybucket')

    # List all buckets
    response = s3.list_buckets()
    s3_buckets_list = response['Buckets']

    assert len(s3_buckets_list) == 1
    assert s3_buckets_list[0]['Name'] == 'mybucket'

if __name__ == '__main__':
    pytest.main()
