from typing import Optional, Sequence

from psycopg2.extras import DictRow
from psycopg2.pool import SimpleConnectionPool
from pypika import PostgreSQLQuery, Order
from pypika.functions import Count
from pypika.queries import QueryBuilder, Table, Query, AliasedQuery
from pypika.terms import Tuple

from config import HOSTNAME, DB_NAME, USERNAME, PASSWORD, PORT_ID, CONNECTION_POOL_MIN_CONNECTIONS, \
    CONNECTION_POOL_MAX_CONNECTIONS
from src.entities.badge_entity import BadgeEntity, BadgeCategory
from src.entities.quest_entity import QuestEntity, QuestType, QuestReward
from src.entities.user_cooldowns_entity import UserCooldownsEntity
from src.entities.user_entity import UserEntity
from src.entities.user_settings_entity import UserSettingsEntity
from src.repositories.user_repository import UserRepository
from src.utils.database_tools import get_cursor, JsonAggregate, JsonBuildArray


class PostgresUserRepository(UserRepository):

    def __init__(self):
        self.connection_pool = SimpleConnectionPool(CONNECTION_POOL_MIN_CONNECTIONS, CONNECTION_POOL_MAX_CONNECTIONS,
                                                    host=HOSTNAME, dbname=DB_NAME, user=USERNAME,
                                                    password=PASSWORD, port=PORT_ID)
        self.fetch_users_query: QueryBuilder = self.build_fetch_users_query()

    @staticmethod
    def table_entry_to_user(table_entry: DictRow) -> UserEntity:
        user_settings_entity = UserSettingsEntity(table_entry["language_id"], table_entry["booster_opening_with_image"],
                                                  table_entry["only_use_stocked_action_with_option"])
        user_cooldowns_entity = UserCooldownsEntity(table_entry["timestamp_for_next_basic_booster"],
                                                    table_entry["timestamp_for_next_promo_booster"],
                                                    table_entry["timestamp_for_next_daily"],
                                                    table_entry["timestamp_for_next_grading"])
        cards = {}
        if table_entry["cards"] is not None:
            cards = {(card_id, grade_name): quantity for (card_id, grade_name, quantity) in table_entry["cards"]}

        quests = []
        if table_entry["quests"] is not None:
            quests = [QuestEntity(QuestType[kind], goal_value, QuestReward[reward_kind], reward_amount,
                                  progress, accomplished, quest_id) for
                      (quest_id, kind, goal_value, progress, reward_kind, reward_amount, accomplished) in
                      table_entry["quests"]]

        return UserEntity(table_entry["id"], table_entry["name_tag"], table_entry["is_banned"],
                          table_entry["last_interaction_date"], table_entry["money"], table_entry["boosters_quantity"],
                          table_entry["promo_boosters_quantity"], table_entry["grading_quantity"], cards,
                          user_settings_entity, user_cooldowns_entity, quests, table_entry["next_daily_quests_refresh"])

    @staticmethod
    def table_entry_to_badge(table_entry: DictRow) -> BadgeEntity:
        return BadgeEntity(table_entry["id"], table_entry["emoji"],
                           BadgeCategory[table_entry["category"]], table_entry["localization_key"])

    @staticmethod
    def build_fetch_users_query() -> QueryBuilder:
        user_table = Table("player")
        user_cooldowns_table = Table("player_cooldowns")
        user_settings_table = Table("player_settings")
        user_card_table = Table("player_card")
        quest_table = Table("player_quest")

        cards_query = Query.from_(user_card_table) \
            .select(user_card_table.player_id,
                    JsonAggregate(JsonBuildArray(user_card_table.card_id,
                                                 user_card_table.grade,
                                                 user_card_table.quantity)).as_("cards"),
                    Count(user_card_table.card_id).distinct().as_("nb_cards")) \
            .groupby(user_card_table.player_id)

        quests_query = Query.from_(quest_table) \
            .select(quest_table.player_id, JsonAggregate(JsonBuildArray(quest_table.id,
                                                                        quest_table.kind,
                                                                        quest_table.goal_value,
                                                                        quest_table.progress,
                                                                        quest_table.reward_kind,
                                                                        quest_table.reward_amount,
                                                                        quest_table.accomplished))
                    .as_("quests")) \
            .groupby(quest_table.player_id)

        return Query.with_(cards_query, "cards_by_player") \
            .with_(quests_query, "quests_by_player") \
            .select(user_table.id, user_table.name_tag,
                    user_table.is_banned, user_table.last_interaction_date, user_table.money,
                    user_table.boosters_quantity, user_table.promo_boosters_quantity,
                    user_table.grading_quantity, user_table.next_daily_quests_refresh,
                    user_cooldowns_table.timestamp_for_next_basic_booster,
                    user_cooldowns_table.timestamp_for_next_promo_booster,
                    user_cooldowns_table.timestamp_for_next_daily,
                    user_cooldowns_table.timestamp_for_next_grading,
                    user_settings_table.language_id,
                    user_settings_table.booster_opening_with_image,
                    user_settings_table.only_use_stocked_action_with_option,
                    AliasedQuery("cards_by_player").cards,
                    AliasedQuery("quests_by_player").quests) \
            .from_(user_table) \
            .inner_join(user_cooldowns_table) \
            .on(user_table.id == user_cooldowns_table.player_id) \
            .inner_join(user_settings_table) \
            .on(user_table.id == user_settings_table.player_id) \
            .left_join(AliasedQuery("cards_by_player")) \
            .on(user_table.id == AliasedQuery("cards_by_player").player_id) \
            .left_join(AliasedQuery("quests_by_player")) \
            .on(user_table.id == AliasedQuery("quests_by_player").player_id)

    def get_all(self) -> Sequence[UserEntity]:
        try:
            with get_cursor(self.connection_pool) as cursor:
                get_all_query: QueryBuilder = self.fetch_users_query
                cursor.execute(get_all_query.get_sql())
                result_set = cursor.fetchall()
                return [self.table_entry_to_user(entry) for entry in result_set]
        except Exception as e:
            print(f"Error while fetching all users: {e}")
        return []

    def get_user(self, user_id: int) -> Optional[UserEntity]:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_table = Table("player")
                get_query: QueryBuilder = self.fetch_users_query.where(user_table.id == user_id)
                cursor.execute(get_query.get_sql())
                entry = cursor.fetchone()
                if entry is None:
                    return None
                return self.table_entry_to_user(entry)
        except Exception as e:
            print(f"Error while getting user {user_id}: {e}")
        return None

    def get_user_badges(self, user_id: int) -> Sequence[BadgeEntity]:
        try:
            with get_cursor(self.connection_pool) as cursor:
                badge_table = Table("badge")
                user_badge_table = Table("player_badge")
                get_query: QueryBuilder = Query.select(badge_table.id, badge_table.emoji, badge_table.category,
                                                       badge_table.localization_key) \
                    .from_(badge_table) \
                    .inner_join(user_badge_table) \
                    .on(badge_table.id == user_badge_table.badge_id) \
                    .where(user_badge_table.player_id == user_id)
                cursor.execute(get_query.get_sql())
                result_set = cursor.fetchall()
                if result_set is None:
                    return []
                return [self.table_entry_to_badge(entry) for entry in result_set]
        except Exception as e:
            print(f"Error while getting user {user_id}: {e}")
        return []

    def save_user(self, user: UserEntity) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_table = Table("player")
                insert_user_query: QueryBuilder = Query.into(user_table) \
                    .insert(user.id, user.name_tag, user.is_banned,
                            user.last_interaction_date, user.money,
                            user.boosters_quantity, user.promo_boosters_quantity,
                            user.grading_quantity, user.next_daily_quests_refresh)
                cursor.execute(insert_user_query.get_sql())

                user_cooldowns_table = Table("player_cooldowns")
                insert_cooldowns_query: QueryBuilder = Query.into(user_cooldowns_table) \
                    .insert(user.id, user.cooldowns.timestamp_for_next_basic_booster,
                            user.cooldowns.timestamp_for_next_promo_booster,
                            user.cooldowns.timestamp_for_next_daily,
                            user.cooldowns.timestamp_for_next_grading)
                cursor.execute(insert_cooldowns_query.get_sql())

                user_settings_table = Table("player_settings")
                insert_settings_query: QueryBuilder = Query.into(user_settings_table) \
                    .insert(user.id, user.settings.language_id,
                            user.settings.booster_opening_with_image,
                            user.settings.only_use_action_from_stock_with_option)
                cursor.execute(insert_settings_query.get_sql())

                return True
        except Exception as e:
            print(f"Error while saving user {user.id}: {e}")
        return False

    def save_user_quests(self, user_id: int, daily_quests: Sequence[QuestEntity]) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_quest_table = Table("player_quest")
                insert_quest_query: QueryBuilder = Query.into(user_quest_table).columns('player_id', 'kind',
                                                                                        'goal_value', 'progress',
                                                                                        'reward_kind', 'reward_amount',
                                                                                        'accomplished')
                for quest in daily_quests:
                    insert_quest_query = insert_quest_query.insert(user_id, quest.kind.name, quest.goal_value,
                                                                   quest.progress, quest.reward_kind.name,
                                                                   quest.reward_amount, quest.accomplished)
                cursor.execute(insert_quest_query.get_sql())

                return True
        except Exception as e:
            print(f"Error while saving quests for user {user_id}: {e}")
        return False

    def update_user(self, user: UserEntity) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_table = Table("player")
                update_user_query: QueryBuilder = Query.update(user_table) \
                    .set(user_table.name_tag, user.name_tag) \
                    .set(user_table.is_banned, user.is_banned) \
                    .set(user_table.last_interaction_date, user.last_interaction_date) \
                    .set(user_table.money, user.money) \
                    .set(user_table.boosters_quantity, user.boosters_quantity) \
                    .set(user_table.promo_boosters_quantity, user.promo_boosters_quantity) \
                    .set(user_table.grading_quantity, user.grading_quantity) \
                    .set(user_table.next_daily_quests_refresh, user.next_daily_quests_refresh) \
                    .where(user_table.id == user.id)
                cursor.execute(update_user_query.get_sql())

                user_cooldowns_table = Table("player_cooldowns")
                update_cooldowns_query: QueryBuilder = Query.update(user_cooldowns_table) \
                    .set(user_cooldowns_table.timestamp_for_next_basic_booster,
                         user.cooldowns.timestamp_for_next_basic_booster) \
                    .set(user_cooldowns_table.timestamp_for_next_promo_booster,
                         user.cooldowns.timestamp_for_next_promo_booster) \
                    .set(user_cooldowns_table.timestamp_for_next_daily, user.cooldowns.timestamp_for_next_daily) \
                    .set(user_cooldowns_table.timestamp_for_next_grading, user.cooldowns.timestamp_for_next_grading) \
                    .where(user_cooldowns_table.player_id == user.id)
                cursor.execute(update_cooldowns_query.get_sql())

                user_settings_table = Table("player_settings")
                update_settings_query: QueryBuilder = Query.update(user_settings_table) \
                    .set(user_settings_table.language_id, user.settings.language_id) \
                    .set(user_settings_table.booster_opening_with_image, user.settings.booster_opening_with_image) \
                    .set(user_settings_table.only_use_stocked_action_with_option,
                         user.settings.only_use_action_from_stock_with_option) \
                    .where(user_settings_table.player_id == user.id)
                cursor.execute(update_settings_query.get_sql())

                return True
        except Exception as e:
            print(f"Error while updating user {user.id}: {e}")
        return False

    def update_user_quests(self, quest_entities: Sequence[QuestEntity], _) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_quest_table = Table("player_quest")
                for quest in quest_entities:
                    update_quest_query: QueryBuilder = Query.update(user_quest_table) \
                        .set(user_quest_table.progress, quest.progress) \
                        .set(user_quest_table.accomplished, quest.accomplished) \
                        .where(user_quest_table.id == quest.id)
                    cursor.execute(update_quest_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while updating status of user quests {quest_entities}: {e}")
        return False

    def set_user_ban(self, user_id: int, is_banned: bool) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_table = Table("player")
                update_user_query: QueryBuilder = Query.update(user_table) \
                    .set(user_table.is_banned, is_banned) \
                    .where(user_table.id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing ban status of user {user_id} to {is_banned}: {e}")
        return False

    def change_money(self, user_id: int, money_change: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_table = Table("player")
                update_user_query: QueryBuilder = Query.update(user_table) \
                    .set(user_table.money, user_table.money + money_change) \
                    .where(user_table.id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing money of user {user_id} by {money_change}: {e}")
        return False

    def change_all_money(self, money_change: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_table = Table("player")
                update_user_query: QueryBuilder = Query.update(user_table) \
                    .set(user_table.money, user_table.money + money_change)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing money of everybody by {money_change}: {e}")
        return False

    def change_basic_boosters_quantity(self, user_id: int, quantity: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_table = Table("player")
                update_user_query: QueryBuilder = Query.update(user_table) \
                    .set(user_table.boosters_quantity,
                         user_table.boosters_quantity + quantity) \
                    .where(user_table.id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing number of basic boosters of {user_id} by {quantity}: {e}")
        return False

    def change_all_basic_boosters_quantity(self, quantity: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_table = Table("player")
                update_user_query: QueryBuilder = Query.update(user_table) \
                    .set(user_table.boosters_quantity,
                         user_table.boosters_quantity + quantity)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing number of basic boosters of everybody by {quantity}: {e}")
        return False

    def change_promo_boosters_quantity(self, user_id: int, quantity: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_table = Table("player")
                update_user_query: QueryBuilder = Query.update(user_table) \
                    .set(user_table.promo_boosters_quantity,
                         user_table.promo_boosters_quantity + quantity) \
                    .where(user_table.id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing number of promo boosters of {user_id} by {quantity}: {e}")
        return False

    def change_all_promo_boosters_quantity(self, quantity: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_table = Table("player")
                update_user_query: QueryBuilder = Query.update(user_table) \
                    .set(user_table.promo_boosters_quantity,
                         user_table.promo_boosters_quantity + quantity)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing number of promo boosters of everybody by {quantity}: {e}")
        return False

    def change_gradings_quantity(self, user_id: int, quantity: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_table = Table("player")
                update_user_query: QueryBuilder = Query.update(user_table) \
                    .set(user_table.grading_quantity,
                         user_table.grading_quantity + quantity) \
                    .where(user_table.id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing number of grading in stock of {user_id} by {quantity}: {e}")
        return False

    def change_user_language(self, user_id: int, new_language_id: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_settings_table = Table("player_settings")
                update_user_query: QueryBuilder = Query.update(user_settings_table) \
                    .set(user_settings_table.language_id,
                         new_language_id) \
                    .where(user_settings_table.player_id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing language of {user_id} to {new_language_id}: {e}")
        return False

    def change_booster_opening_with_image_by_default(self, user_id: int,
                                                     new_booster_opening_with_image_value: bool) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_settings_table = Table("player_settings")
                update_user_query: QueryBuilder = Query.update(user_settings_table) \
                    .set(user_settings_table.booster_opening_with_image,
                         new_booster_opening_with_image_value) \
                    .where(user_settings_table.player_id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing opening booster mode of {user_id} to {new_booster_opening_with_image_value}: "
                  f"{e}")
        return False

    def change_only_use_booster_stock_with_option(self, user_id: int,
                                                  new_only_use_booster_stock_with_option_value: bool) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_settings_table = Table("player_settings")
                update_user_query: QueryBuilder = Query.update(user_settings_table) \
                    .set(user_settings_table.only_use_stocked_action_with_option,
                         new_only_use_booster_stock_with_option_value) \
                    .where(user_settings_table.player_id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing restricted use of stocked action for {user_id} "
                  f"to {new_only_use_booster_stock_with_option_value}: {e}")
        return False

    def change_basic_booster_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_cooldowns_table = Table("player_cooldowns")
                update_user_query: QueryBuilder = Query.update(user_cooldowns_table) \
                    .set(user_cooldowns_table.timestamp_for_next_basic_booster,
                         updated_timestamp_for_cooldown) \
                    .where(user_cooldowns_table.player_id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing timestamp cooldown for basic booster for {user_id} "
                  f"to {updated_timestamp_for_cooldown}: {e}")
        return False

    def change_promo_booster_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_cooldowns_table = Table("player_cooldowns")
                update_user_query: QueryBuilder = Query.update(user_cooldowns_table) \
                    .set(user_cooldowns_table.timestamp_for_next_promo_booster,
                         updated_timestamp_for_cooldown) \
                    .where(user_cooldowns_table.player_id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing timestamp cooldown for promo booster for {user_id} "
                  f"to {updated_timestamp_for_cooldown}: {e}")
        return False

    def change_daily_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_cooldowns_table = Table("player_cooldowns")
                update_user_query: QueryBuilder = Query.update(user_cooldowns_table) \
                    .set(user_cooldowns_table.timestamp_for_next_daily,
                         updated_timestamp_for_cooldown) \
                    .where(user_cooldowns_table.player_id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing timestamp cooldown for daily for {user_id} "
                  f"to {updated_timestamp_for_cooldown}: {e}")
        return False

    def change_grading_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                user_cooldowns_table = Table("player_cooldowns")
                update_user_query: QueryBuilder = Query.update(user_cooldowns_table) \
                    .set(user_cooldowns_table.timestamp_for_next_grading,
                         updated_timestamp_for_cooldown) \
                    .where(user_cooldowns_table.player_id == user_id)
                cursor.execute(update_user_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while changing timestamp cooldown for grading for {user_id} "
                  f"to {updated_timestamp_for_cooldown}: {e}")
        return False

    def add_card_to_collection(self, user_id: int, card_id: str, grade_name: str = "UNGRADED") -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                player_card_table = Table("player_card")
                insert_card_query: QueryBuilder = Query.into(player_card_table) \
                    .insert(user_id, card_id, grade_name, 1) \
                    .on_conflict(player_card_table.player_id, player_card_table.card_id, player_card_table.grade) \
                    .do_update(player_card_table.quantity, player_card_table.quantity + 1)
                cursor.execute(insert_card_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while adding card {card_id} with grade {grade_name} to collection of user {user_id}: {e}")
        return False

    def add_cards_to_collection(self, user_id: int, card_ids_with_grade: list[tuple[str, str]]) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                player_card_table = Table("player_card")
                insert_cards_query: QueryBuilder = PostgreSQLQuery.into(player_card_table)
                for card_id, grade_name in card_ids_with_grade:
                    insert_cards_query: QueryBuilder = insert_cards_query.insert(user_id, card_id,
                                                                                 grade_name, 1)
                insert_cards_query: QueryBuilder = insert_cards_query.on_conflict(player_card_table.player_id,
                                                                                  player_card_table.card_id,
                                                                                  player_card_table.grade) \
                    .do_update(player_card_table.quantity,
                               player_card_table.quantity + 1)
                cursor.execute(insert_cards_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while adding cards {card_ids_with_grade} to collection of user {user_id}: {e}")
        return False

    def remove_card_from_collection(self, user_id: int, card_id: str, grade_name: str = "UNGRADED") -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                player_card_table = Table("player_card")
                delete_card_query: QueryBuilder = Query.from_(player_card_table).delete() \
                    .where((player_card_table.user_id == user_id & player_card_table.card_id == card_id) &
                           player_card_table.grade == grade_name) \
                    .where(player_card_table.quantity == 1)
                cursor.execute(delete_card_query.get_sql())

                if cursor.rowcount == 0:
                    update_card_query: QueryBuilder = Query.update(player_card_table) \
                        .set(player_card_table.quantity,
                             player_card_table.quantity - 1) \
                        .where((player_card_table.user_id == user_id &
                                player_card_table.card_id == card_id) &
                               player_card_table.grade == grade_name)
                    cursor.execute(update_card_query.get_sql())

                    if cursor.rowcount == 0:
                        return False
                return True
        except Exception as e:
            print(f"Error while removing card {card_id} with grade {grade_name} from collection of user {user_id}: {e}")
        return False

    def remove_cards_from_collection(self, user_id: int, card_ids_with_grade: list[tuple[str, str]]) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                player_card_table = Table("player_card")
                delete_card_query: QueryBuilder = Query.from_(player_card_table).delete() \
                    .where(player_card_table.player_id == user_id) \
                    .where(Tuple(player_card_table.card_id, player_card_table.grade).isin(card_ids_with_grade)) \
                    .where(player_card_table.quantity == 1)
                cursor.execute(delete_card_query.get_sql())

                count_affected_rows = cursor.rowcount
                if count_affected_rows < len(card_ids_with_grade):
                    update_card_query: QueryBuilder = Query.update(player_card_table) \
                        .set(player_card_table.quantity,
                             player_card_table.quantity - 1) \
                        .where(player_card_table.player_id == user_id) \
                        .where(Tuple(player_card_table.card_id, player_card_table.grade)
                               .isin(card_ids_with_grade))
                    cursor.execute(update_card_query.get_sql())

                    count_affected_rows += cursor.rowcount
                    if count_affected_rows < len(card_ids_with_grade):
                        return False
                return True
        except Exception as e:
            print(f"Error while removing cards {card_ids_with_grade} from collection of user {user_id}: {e}")
        return False

    def remove_user_quests(self, user_id: int) -> bool:
        try:
            with get_cursor(self.connection_pool) as cursor:
                quest_table = Table("player_quest")
                delete_user_quests_query: QueryBuilder = Query.from_(quest_table) \
                    .delete() \
                    .where(quest_table.player_id == user_id)
                cursor.execute(delete_user_quests_query.get_sql())
                return True
        except Exception as e:
            print(f"Error while removing old quests for user {user_id}: {e}")
        return False

    def get_top_users_by_cards(self, number: int) -> Sequence[UserEntity]:
        try:
            with get_cursor(self.connection_pool) as cursor:
                get_all_query: QueryBuilder = self.fetch_users_query.orderby(AliasedQuery("cards_by_player").nb_cards,
                                                                             order=Order.desc) \
                    .limit(number)
                cursor.execute(get_all_query.get_sql())
                result_set = cursor.fetchall()
                return [self.table_entry_to_user(entry) for entry in result_set]
        except Exception as e:
            print(f"Error while fetching all users: {e}")
        return []
