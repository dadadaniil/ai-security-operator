CREATE TABLE refresh_tokens
(
    id          bigserial PRIMARY KEY,
    user_id     bigint                   NOT NULL,
    token       text UNIQUE              NOT NULL,
    expiry_date timestamp with time zone NOT NULL
);

ALTER TABLE refresh_tokens
    ADD FOREIGN KEY (user_id) REFERENCES users (id);
