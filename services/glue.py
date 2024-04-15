import logging
from typing import Dict, List

import parsers
import tools
from settings import LOGGER_NAME, NO_VALUE

args = parsers.programm_args
aws_session = tools.init_connection(profile_name=args.profile)

LOGGER = logging.getLogger(LOGGER_NAME)


def get_glue_db_list() -> List[str]:
    glue_client = aws_session.client('glue')
    db_list = list()
    paginator = glue_client.get_paginator('get_databases').paginate()
    LOGGER.info("All personal DBs, started from adl_personal, will be skipped")
    LOGGER.info("Getting the full list of Glue DBs...")
    for page in paginator:
        for database in page['DatabaseList']:
            if "adl_personal" in database['Name']:
                LOGGER.debug(f"Skipping {database['Name']}")
                continue
            db_list.append(database['Name'])
    LOGGER.info(f"Found {len(db_list)} Glue databases.")
    return db_list


def get_glue_db_tables(database_name) -> List[Dict]:
    glue_client = aws_session.client('glue')
    data = list()
    paginator = glue_client.get_paginator('get_tables').paginate(DatabaseName=database_name)
    for page in paginator:
        for table in page['TableList']:
            data.append(
                {
                    'db_name': database_name,
                    'table_name': table['Name'],
                    'location': table['StorageDescriptor'].get('Location', NO_VALUE)
                }
            )
    return data

@tools.show_as_table
def get_glue_info():
    glue_db_list = get_glue_db_list()
    return tools.run_thread(get_glue_db_tables, glue_db_list)

