CREATE TYPE badge_category AS ENUM ('GENERAL', 'COLLECTION', 'ACTION' , 'EVENT');
CREATE TABLE badge (
    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    emoji varchar(128) NOT NULL,
    category badge_category NOT NULL,
    localization_key varchar(128) NOT NULL
);
INSERT INTO badge(emoji, category, localization_key) VALUES (':fire:', 'GENERAL', 'beta_tester');

CREATE TABLE player_badge (
    player_id bigint NOT NULL REFERENCES player,
    badge_id int NOT NULL REFERENCES badge,
    PRIMARY KEY (player_id, badge_id)
);
