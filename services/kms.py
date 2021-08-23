## TO DO: Add STate (used or unused)

def get_kms_info(aws_session):
    client = aws_session.client('kms')
    kms_keys = []
    paginator = client.get_paginator('list_aliases')
    for i in paginator.paginate():
        for a in i['Aliases']:
            kms_info = dict()
            kms_info['Name'] = a['AliasName']
            kms_info['ARN'] = a['AliasArn']
            if a['AliasName'].find("alias/aws") != -1:
                kms_info['Type'] = "AWS"
            else:
                kms_info['Type'] = "Custom"
            kms_keys.append(kms_info)
    return kms_keys