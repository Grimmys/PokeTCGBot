CREATE TABLE player_booster (
    player_id bigint NOT NULL REFERENCES player,
    booster_id varchar(64) NOT NULL,
    quantity int NOT NULL,
    PRIMARY KEY (player_id, booster_id)
);
