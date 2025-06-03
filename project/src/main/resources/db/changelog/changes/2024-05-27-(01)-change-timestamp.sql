ALTER TABLE comments
    ALTER COLUMN creation_date
        SET DATA TYPE timestamp with time zone USING creation_date AT TIME ZONE 'UTC';

ALTER TABLE comments
    ALTER COLUMN update_date
        SET DATA TYPE timestamp with time zone USING update_date AT TIME ZONE 'UTC';

ALTER TABLE tasks
    ALTER COLUMN creation_date
        SET DATA TYPE timestamp with time zone USING creation_date AT TIME ZONE 'UTC';

ALTER TABLE tasks
    ALTER COLUMN expected_delivery_time
        SET DATA TYPE timestamp with time zone USING expected_delivery_time AT TIME ZONE 'UTC';

ALTER TABLE tasks
    ALTER COLUMN update_date
        SET DATA TYPE timestamp with time zone USING update_date AT TIME ZONE 'UTC';

ALTER TABLE users
    ALTER COLUMN creation_date
        SET DATA TYPE timestamp with time zone USING creation_date AT TIME ZONE 'UTC';

ALTER TABLE users
    ALTER COLUMN update_date
        SET DATA TYPE timestamp with time zone USING update_date AT TIME ZONE 'UTC';

ALTER TABLE confirmation_token
    ALTER COLUMN created_date
        SET DATA TYPE timestamp with time zone USING created_date AT TIME ZONE 'UTC';
