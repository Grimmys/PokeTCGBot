from typing import Sequence, Optional

from psycopg2.extras import DictRow
from psycopg2.pool import SimpleConnectionPool
from pypika import Table, Query, Parameter
from pypika.queries import QueryBuilder

from config import HOSTNAME, DB_NAME, USERNAME, PASSWORD, PORT_ID, CONNECTION_POOL_MIN_CONNECTIONS, \
    CONNECTION_POOL_MAX_CONNECTIONS
from src.entities.suggestion_entity import SuggestionEntity
from src.repositories.suggestion_repository import SuggestionRepository
from src.utils.database_tools import JsonBuildArray, JsonAggregate, get_cursor


class PostgresSuggestionRepository(SuggestionRepository):

    def __init__(self):
        self.connection_pool = SimpleConnectionPool(CONNECTION_POOL_MIN_CONNECTIONS, CONNECTION_POOL_MAX_CONNECTIONS,
                                                    host=HOSTNAME, dbname=DB_NAME, user=USERNAME,
                                                    password=PASSWORD, port=PORT_ID)
        self.fetch_suggestions_query = self.build_fetch_suggestions_query()
        self.remove_vote_query = self.build_remove_vote_query()

    @staticmethod
    def table_entry_to_entity(table_entry: DictRow) -> SuggestionEntity:
        up_votes = set(voter_id for (voter_id, is_positive) in table_entry["votes"] if is_positive)
        down_votes = set(voter_id for (voter_id, is_positive) in table_entry["votes"]
                         if is_positive is not None and not is_positive)
        return SuggestionEntity(table_entry["author"], table_entry["content"], table_entry["id"], up_votes, down_votes)

    @staticmethod
    def build_fetch_suggestions_query():
        suggestion_table = Table("suggestion")
        suggestion_vote_table = Table("suggestion_vote")
        return Query.select(suggestion_table.id, suggestion_table.author,
                            suggestion_table.content,
                            JsonAggregate(JsonBuildArray(suggestion_vote_table.voter_id,
                                                         suggestion_vote_table.is_positive))
                            .as_("votes")) \
            .from_(suggestion_table) \
            .left_join(suggestion_vote_table) \
            .on(suggestion_table.id == suggestion_vote_table.suggestion_id) \
            .groupby(suggestion_table.id)

    @staticmethod
    def build_remove_vote_query():
        suggestion_vote_table = Table("suggestion_vote")
        return Query.from_(suggestion_vote_table).delete().where(
            (suggestion_vote_table.voter_id == Parameter("%(user_id)s")) &
            (suggestion_vote_table.suggestion_id == Parameter("%(suggestion_id)s")))

    @staticmethod
    def build_add_vote_query(is_positive: bool):
        suggestion_vote_table = Table("suggestion_vote")
        return Query.into(suggestion_vote_table).insert(
            Parameter("%(suggestion_id)s"),
            Parameter("%(user_id)s"),
            is_positive)

    def get_all(self) -> Sequence[SuggestionEntity]:
        try:
            with get_cursor(self.connection_pool) as cursor:
                query: QueryBuilder = self.fetch_suggestions_query
                cursor.execute(query.get_sql())
                result_set = cursor.fetchall()
                return [self.table_entry_to_entity(entry) for entry in result_set]
        except Exception as e:
            print(f"Error while fetching all suggestions: {e}")
        return []

    def save_suggestion(self, suggestion: SuggestionEntity) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                suggestion_table = Table("suggestion")
                insert_query: QueryBuilder = Query.into(suggestion_table).insert(Parameter("%(id)s"),
                                                                                 Parameter("%(author)s"),
                                                                                 Parameter("%(content)s"))
                cursor.execute(insert_query.get_sql(),
                               {"id": suggestion.id, "author": suggestion.author, "content": suggestion.content})
            return True
        except Exception as e:
            print(f"Error while saving the suggestion '{suggestion.content}': {e}")
        return False

    def remove_suggestion(self, suggestion_id: str) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                suggestion_table = Table("suggestion")
                delete_query: QueryBuilder = Query.from_(suggestion_table).delete() \
                                                  .where(suggestion_table.id == suggestion_id)
                cursor.execute(delete_query.get_sql())
            return True
        except Exception as e:
            print(f"Error while removing suggestion with id {suggestion_id}: {e}")
        return False

    def switch_up_vote_for(self, user_id: int, suggestion_id: str) -> Optional[SuggestionEntity]:
        try:
            with get_cursor(self.connection_pool) as cursor:
                suggestion_table = Table("suggestion")
                get_query: QueryBuilder = self.fetch_suggestions_query.where(suggestion_table.id == suggestion_id)
                cursor.execute(get_query.get_sql())
                entry = cursor.fetchone()
                suggestion_entity = PostgresSuggestionRepository.table_entry_to_entity(entry)

                if user_id in suggestion_entity.down_votes:
                    return None

                if user_id in suggestion_entity.up_votes:
                    suggestion_entity.up_votes.remove(user_id)
                    update_query: QueryBuilder = self.remove_vote_query
                else:
                    suggestion_entity.up_votes.add(user_id)
                    update_query: QueryBuilder = self.build_add_vote_query(True)
                cursor.execute(update_query.get_sql(), {"user_id": user_id, "suggestion_id": suggestion_id})
                return suggestion_entity
        except Exception as e:
            print(f"Error while updating upvoting of suggestion with id {suggestion_id} by user {user_id}: {e}")
        return None

    def switch_down_vote_for(self, user_id: int, suggestion_id: str) -> Optional[SuggestionEntity]:
        try:
            with get_cursor(self.connection_pool) as cursor:
                suggestion_table = Table("suggestion")
                get_query: QueryBuilder = self.fetch_suggestions_query.where(suggestion_table.id == suggestion_id)
                cursor.execute(get_query.get_sql())
                entry = cursor.fetchone()
                suggestion_entity = PostgresSuggestionRepository.table_entry_to_entity(entry)

                if user_id in suggestion_entity.up_votes:
                    return None

                if user_id in suggestion_entity.down_votes:
                    suggestion_entity.down_votes.remove(user_id)
                    update_query: QueryBuilder = self.remove_vote_query
                else:
                    suggestion_entity.down_votes.add(user_id)
                    update_query: QueryBuilder = self.build_add_vote_query(False)
                cursor.execute(update_query.get_sql(), {"user_id": user_id, "suggestion_id": suggestion_id})
                return suggestion_entity
        except Exception as e:
            print(f"Error while updating downvoting of suggestion with id {suggestion_id} by user {user_id}: {e}")
        return None
