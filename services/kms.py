## TO DO: Add STate (used or unused)
import parsers
import tools

args = parsers.programm_args
aws_session = tools.init_connection(profile_name=args.profile)

@tools.show_as_table_dec
def get_kms_info():
    client = aws_session.client('kms')
    kms_keys = []
    paginator = client.get_paginator('list_aliases')
    for i in paginator.paginate():
        for key in i['Aliases']:
            kms_info = dict()
            if key['AliasName'].find("alias/aws") != -1:
                continue
            kms_info['Name'] = key['AliasName']
            kms_info['ARN'] = key['AliasArn']
            key_more_info = client.describe_key(KeyId=key['TargetKeyId'])
            kms_info['Usage'] = key_more_info['KeyMetadata']['KeyUsage']
            kms_info['State'] = key_more_info['KeyMetadata']['KeyState']
            kms_info['Algorithm'] = key_more_info['KeyMetadata']['EncryptionAlgorithms']
            kms_keys.append(kms_info)
    return kms_keys