-- Remove the SQLite foreign data wrapper
DROP SCHEMA IF EXISTS frc_etl CASCADE;
DROP SERVER IF EXISTS frc_etl_source;
DROP EXTENSION IF EXISTS sqlite_fdw;
