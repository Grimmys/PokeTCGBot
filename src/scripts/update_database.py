import glob
import os
from pathlib import Path
from typing import Sequence

from pypika import Query
from pypika.queries import QueryBuilder, Table

from src.utils.database_tools import get_cursor


def update_database_schema(connection_pool):
    try:
        with get_cursor(connection_pool) as cursor:
            patch_version_table = Table("patch_version")
            get_patch_version_query: QueryBuilder = Query.select(patch_version_table.patch_id) \
                .from_(patch_version_table) \
                .limit(1)
            cursor.execute(get_patch_version_query.get_sql())
            current_database_patch_version: int = cursor.fetchone()["patch_id"]

            application_patches_not_run: Sequence[str] = list(
                filter(lambda patch_name: _get_patch_number(patch_name) > current_database_patch_version,
                       [Path(full_path).stem for full_path in
                        glob.glob(os.getcwd() + "/database/patches/*.sql")]))

            for patch_name in application_patches_not_run:
                patch_queries = get_queries_from_file(os.path.join(os.getcwd(), "database", "patches",
                                                                   patch_name + ".sql"))

                for query in patch_queries:
                    cursor.execute(query)

                patch_number = _get_patch_number(patch_name)
                if patch_number > current_database_patch_version:
                    update_patch_version_query: QueryBuilder = Query.update(patch_version_table).set(
                        patch_version_table.patch_id, patch_number)
                    cursor.execute(update_patch_version_query.get_sql())
                    current_database_patch_version = patch_number
            return True
    except Exception as e:
        print(f"Error while updating database schema: {e}")
    return False


def get_queries_from_file(filename: str) -> Sequence[str]:
    with open(filename, "r") as file:
        raw_sql = file.read().replace("\n", "")

    return [query for query in raw_sql.split(";") if query != ""]


def _get_patch_number(patch_name: str) -> int:
    return int(patch_name.split("_")[-1])
