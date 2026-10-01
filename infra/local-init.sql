-- Synthetic local fixtures only, not T-003b production role bootstrap.
CREATE ROLE aap_migration LOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE aap_runtime LOGIN NOSUPERUSER NOBYPASSRLS;
CREATE DATABASE aap_foundation OWNER aap_migration;
\connect aap_foundation
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE aap_migration IN SCHEMA public
  GRANT SELECT ON TABLES TO aap_runtime;
