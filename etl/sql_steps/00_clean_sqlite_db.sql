-- Remove unnecessary tables from SQLite export so it can be safely shared
-- This runs in SQLite where all the others run in PostgreSQL

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

-- can't write to SQLite through foreign data wrapper
-- Pre-clean the tags here

-- Make unconflicting uppercase tags lowercase
UPDATE taggit_tag
SET name = lower(subquery.name)
FROM (
    SELECT
        id,
        name
    FROM taggit_tag
    WHERE NOT (lower(name) = name) -- at least one char is uppercase
    AND slug not like '%_1' -- not a conflicting bad tag
) AS subquery
WHERE taggit_tag.id = subquery.id;


-- Repair broken tags due to uppercase or conflicts
UPDATE taggit_taggeditem
SET tag_id = good_id
FROM (
    SELECT
        gt.id AS good_id,
        bt.id AS bad_id
    FROM taggit_tag AS bt
    JOIN taggit_tag AS gt
    ON lower(bt.name) = gt.name
    WHERE bt.slug like '%_1'
    AND gt.slug not like '%_1'
)
WHERE tag_id = bad_id;

-- delete duplicated tag assignments
DELETE FROM taggit_taggeditem
WHERE id NOT IN (
    SELECT min(id)
    FROM taggit_taggeditem
    GROUP BY tag_id, object_id, content_type_id
);

-- delete bad tags entirely
DELETE from taggit_tag WHERE slug like '%_1';

-- Set times on news to '20:00' if they are '00:00'
UPDATE news_news
SET pub_date = substr(pub_date, 0, 12) || '20:00:00'
WHERE substr(pub_date,12) = '00:00:00';