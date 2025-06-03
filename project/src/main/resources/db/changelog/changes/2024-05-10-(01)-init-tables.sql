CREATE TABLE types_of_comments
(
    id          bigserial PRIMARY KEY,
    name        text NOT NULL,
    description text NOT NULL
);

CREATE TABLE types_of_contribution
(
    id          bigserial PRIMARY KEY,
    name        text NOT NULL,
    description text NOT NULL
);

CREATE TABLE task_tags
(
    task_id bigint NOT NULL,
    tag_id  bigint NOT NULL
);

CREATE TABLE tags
(
    id   bigserial PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE roles
(
    id          bigserial PRIMARY KEY,
    name        text NOT NULL,
    description text NOT NULL
);

CREATE TABLE assigned
(
    task_id bigint NOT NULL,
    user_id bigint NOT NULL
);

CREATE TABLE comments
(
    id                 bigserial PRIMARY KEY,
    task_id            bigint    NOT NULL,
    user_id            bigint    NOT NULL,
    creation_date      timestamp NOT NULL,
    description        text      NOT NULL,
    type_of_comment_id bigint    NOT NULL,
    update_date        timestamp NOT NULL
);

CREATE TABLE tasks
(
    id                      bigserial PRIMARY KEY,
    creator_id              bigint    NOT NULL,
    creation_date           timestamp NOT NULL,
    title                   text      NOT NULL,
    description             text      NOT NULL,
    budget                  decimal   NOT NULL,
    type_of_contribution_id bigint    NOT NULL,
    contacts                text      NOT NULL,
    expected_delivery_time  timestamp NOT NULL,
    update_date             timestamp NOT NULL
);

CREATE TABLE users
(
    id            bigserial PRIMARY KEY,
    first_name    text        NOT NULL,
    last_name     text        NOT NULL,
    email         text UNIQUE NOT NULL,
    verified      boolean     NOT NULL,
    password      text        NOT NULL,
    role_id       bigint      NOT NULL,
    rating        bigint      NOT NULL,
    creation_date timestamp   NOT NULL,
    balance       bigint      NOT NULL,
    update_date   timestamp   NOT NULL
);

CREATE TABLE confirmation_token
(
    id                 bigserial PRIMARY KEY,
    confirmation_token text          NOT NULL,
    created_date       timestamp     NOT NULL,
    user_id            bigint UNIQUE NOT NULL
);

ALTER TABLE task_tags
    ADD FOREIGN KEY (task_id) REFERENCES tasks (id);
ALTER TABLE task_tags
    ADD FOREIGN KEY (tag_id) REFERENCES tags (id);

ALTER TABLE assigned
    ADD FOREIGN KEY (task_id) REFERENCES tasks (id);
ALTER TABLE assigned
    ADD FOREIGN KEY (user_id) REFERENCES users (id);

ALTER TABLE comments
    ADD FOREIGN KEY (task_id) REFERENCES tasks (id);
ALTER TABLE comments
    ADD FOREIGN KEY (user_id) REFERENCES users (id);
ALTER TABLE comments
    ADD FOREIGN KEY (type_of_comment_id) REFERENCES types_of_comments (id);

ALTER TABLE tasks
    ADD FOREIGN KEY (creator_id) REFERENCES users (id);
ALTER TABLE tasks
    ADD FOREIGN KEY (type_of_contribution_id) REFERENCES types_of_contribution (id);

ALTER TABLE users
    ADD FOREIGN KEY (role_id) REFERENCES roles (id);

ALTER TABLE confirmation_token
    ADD FOREIGN KEY (user_id) REFERENCES users (id);
