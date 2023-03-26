CREATE TABLE player (
    id bigint PRIMARY KEY,
    name_tag varchar(1024) NOT NULL,
    is_banned boolean NOT NULL,
    last_interaction_date int NOT NULL,
    money int NOT NULL,
    boosters_quantity int NOT NULL,
    promo_boosters_quantity int NOT NULL,
    grading_quantity int NOT NULL,
    next_daily_quests_refresh int NOT NULL
);

CREATE TABLE player_settings (
    player_id bigint PRIMARY KEY NOT NULL REFERENCES player,
    language_id int NOT NULL,
    booster_opening_with_image boolean NOT NULL,
    only_use_stocked_action_with_option boolean NOT NULL
);

CREATE TABLE player_cooldowns (
    player_id bigint PRIMARY KEY NOT NULL REFERENCES player,
    timestamp_for_next_basic_booster int NOT NULL,
    timestamp_for_next_promo_booster int NOT NULL,
    timestamp_for_next_daily int NOT NULL,
    timestamp_for_next_grading int NOT NULL
);

CREATE TYPE quest_type AS ENUM ('BOOSTER', 'GRADE', 'DAILY_CLAIM');
CREATE TYPE quest_reward AS ENUM ('BASIC_BOOSTER', 'PROMO_BOOSTER', 'MONEY');
CREATE TABLE player_quest (
    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    player_id bigint NOT NULL REFERENCES player,
    kind quest_type NOT NULL,
    goal_value int NOT NULL,
    progress int NOT NULL,
    reward_kind quest_reward NOT NULL,
    reward_amount int NOT NULL,
    accomplished boolean NOT NULL
);

CREATE TYPE grade_type AS ENUM ('UNGRADED', 'POOR', 'AVERAGE', 'GOOD', 'EXCELLENT');
CREATE TABLE player_card (
    player_id bigint NOT NULL REFERENCES player,
    card_id varchar(64) NOT NULL,
    grade grade_type NOT NULL,
    quantity int NOT NULL,
    PRIMARY KEY (player_id, card_id, grade)
);
CREATE INDEX ON player_card (
    card_id,
    grade
);


CREATE TABLE suggestion (
    id varchar(128) PRIMARY KEY,
    author varchar(1024) NOT NULL,
    content text NOT NULL
);

CREATE TABLE suggestion_vote (
    suggestion_id varchar(128) NOT NULL REFERENCES suggestion ON DELETE CASCADE,
    voter_id bigint NOT NULL REFERENCES player,
    is_positive boolean NOT NULL,
    PRIMARY KEY (suggestion_id, voter_id)
);
