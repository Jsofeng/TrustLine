-- Development-only roles. Production credentials must be provisioned outside source control.
-- Think of this file as creating employees and assigning job permissions.
CREATE ROLE trustline_app LOGIN PASSWORD 'trustline_app_password' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
CREATE ROLE trustline_evaluator LOGIN PASSWORD 'trustline_evaluator_password' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;


-- CREATE ROLE trustline_evaluator: Makes a new user or group account named trustline_evaluator.
-- LOGIN: Lets this user log in to the database system.
-- PASSWORD 'trustline_evaluator_password': Sets the secret password for the user.
-- NOSUPERUSER: Keeps the user from having full system control.
-- NOCREATEDB: Stops the user from making new databases.
-- NOCREATEROLE: Stops the user from making new users or roles.
-- NOINHERIT: Prevents the user from automatically getting permissions from other groups or roles they join.

CREATE DATABASE trustline_test;
GRANT CONNECT ON DATABASE trustline TO trustline_app, trustline_evaluator;
GRANT CONNECT ON DATABASE trustline_test TO trustline_app, trustline_evaluator;