-- Remove unnecessary tables from SQLite export so it can be safely shared
-- NOTE: Run this in sqlite, not in PostgreSQL with fdw
-- ```
-- sqlite3 frc_old.db
-- > .read 00_clean_sqlite_db.sql
-- ```
DROP TABLE IF EXISTS auth_group;
DROP TABLE IF EXISTS auth_group_permissions;
DROP TABLE IF EXISTS auth_permission;
DROP TABLE IF EXISTS auth_user;
DROP TABLE IF EXISTS auth_user_groups;
DROP TABLE IF EXISTS auth_user_user_permissions;
DROP TABLE IF EXISTS celery_taskmeta;
DROP TABLE IF EXISTS celery_tasksetmeta;
DROP TABLE IF EXISTS django_admin_log;
DROP TABLE IF EXISTS django_session;
DROP TABLE IF EXISTS django_site;
DROP TABLE IF EXISTS djcelery_crontabschedule;
DROP TABLE IF EXISTS djcelery_intervalschedule;
DROP TABLE IF EXISTS djcelery_periodictask;
DROP TABLE IF EXISTS djcelery_periodictasks;
DROP TABLE IF EXISTS djcelery_taskstate;
DROP TABLE IF EXISTS djcelery_workerstate;
DROP TABLE IF EXISTS easy_thumbnails_source;
DROP TABLE IF EXISTS easy_thumbnails_thumbnail;
DROP TABLE IF EXISTS robots_rule;
DROP TABLE IF EXISTS robots_rule_allowed;
DROP TABLE IF EXISTS robots_rule_disallowed;
DROP TABLE IF EXISTS robots_rule_sites;
DROP TABLE IF EXISTS robots_url;
DROP TABLE IF EXISTS south_migrationhistory;
