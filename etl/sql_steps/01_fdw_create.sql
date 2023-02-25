-- Create the SQLite foreign data wrapper
SET client_min_messages TO WARNING;
CREATE EXTENSION IF NOT EXISTS sqlite_fdw;
CREATE SERVER IF NOT EXISTS frc_etl_source FOREIGN DATA WRAPPER sqlite_fdw OPTIONS (database %s);
CREATE SERVER IF NOT EXISTS frc_forum_source FOREIGN DATA WRAPPER sqlite_fdw OPTIONS (database %s);
CREATE SCHEMA IF NOT EXISTS frc_etl;
IMPORT FOREIGN SCHEMA public FROM SERVER frc_etl_source INTO frc_etl;
IMPORT FOREIGN SCHEMA public FROM SERVER frc_forum_source INTO frc_etl;
