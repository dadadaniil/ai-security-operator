INSERT INTO roles (name, description)
VALUES ('CLIENT', 'I''m client, I have a task to do'),
       ('STUDENT', 'I''m student, I''m looking for task');

INSERT INTO public.users (first_name, last_name, email, verified, password, role_id,
                          rating, creation_date, balance, update_date)
VALUES ('Daniil', 'Anishchanka', 'anishchanka.daniil@student.ehu.lt', true,
        '$2a$10$8sTRo8brT.e1gjZJ10CcqOTqA8f0gF9xNYDPdE/NIrYq837b6uYoW', 1, 1,
        '2024-04-09 20:00:00.000000', 0, '2024-03-09 19:56:31.000001'),
       ('John', 'Doe', 'john.doe@example.com', false, '$2a$10$8sTRo8brT.e1gjZJ10CcqOTqA8f0gF9xNYDPdE/NIrYq837b6uYoW', 1,
        1,
        '2018-04-09 20:00:00.000000', 0, '2024-04-09 20:00:00.000001'),
       ('Jane', 'Smith', 'jane.smith@example.com', false,
        '$2a$10$8sTRo8brT.e1gjZJ10CcqOTqA8f0gF9xNYDPdE/NIrYq837b6uYoW', 2, 1,
        '2024-04-09 20:00:00.000000', 0, '2024-04-09 20:00:00.000001'),
       ('Robert', 'Johnson', 'robert.johnson@example.com', true,
        '$2a$10$8sTRo8brT.e1gjZJ10CcqOTqA8f0gF9xNYDPdE/NIrYq837b6uYoW', 1, 1,
        '2024-04-09 20:00:00.000000', 0, '2024-04-09 20:00:00.000001'),
       ('Michael', 'Williams', 'michael.williams@example.com', false,
        '$2a$10$8sTRo8brT.e1gjZJ10CcqOTqA8f0gF9xNYDPdE/NIrYq837b6uYoW', 1, 1,
        '2024-04-09 20:00:00.000000', 0, '2024-03-13 19:56:31.000001'),
       ('Password is', 'A1234567!', 'linda.brown@example.com', true,
        '$2a$10$8sTRo8brT.e1gjZJ10CcqOTqA8f0gF9xNYDPdE/NIrYq837b6uYoW', 2, 1,
        '2020-04-09 20:00:00.000000', 0, '2024-04-09 20:00:00.000001');

INSERT INTO public.types_of_contribution (name, description)
VALUES ('Single performer', 'Your task will be performed by a single person.');

INSERT INTO public.types_of_contribution (name, description)
VALUES ('Team of workers', 'A team of several people will be dedicated to the task.');

INSERT INTO tags (name)
VALUES ('UI/UX Design'),
       ('JavaScript'),
       ('ReactJS'),
       ('Angular'),
       ('.Net'),
       ('C#'),
       ('Java'),
       ('Copywriting'),
       ('Manual quality assurance'),
       ('Automation quality assurance'),
       ('Document management'),
       ('Content management'),
       ('Languages'),
       ('Artificial intelligence'),
       ('Creativity'),
       ('School specialist''s assistance'),
       ('Other');
