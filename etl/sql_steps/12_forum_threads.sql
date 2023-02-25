-- Put correct forum thread URLs in all the right places

-- Populate known links for old forum
WITH old_forum_connections AS (
    SELECT
        trim(COALESCE(NULLIF(of.title,''), sc.title)) AS oldforum_title,
        trim(sc.title) AS new_content_title,
        CONCAT(
            'https://forum.frontrowcrew.com/index.php?p=/discussion/',
            eir.source_record->>'forumid',
            '/'
        ) AS forum_url,
        eir.new_id AS new_content_id,
        pe.id AS podcast_episode_id
    FROM etl_importrecord AS eir
    LEFT JOIN frc_etl.oldforum AS of
        ON of.id = (eir.source_record->>'forumid')::int
    JOIN shows_content AS sc
        ON eir.new_id = sc.id
    LEFT JOIN podcasts_podcastepisode AS pe
        ON pe.id = sc.podcast_episode_id
    WHERE eir.old_table_name in ('podcast_episode', 'videos_video')
    AND eir.new_table_name = 'shows_content'
    AND sc.pub_time < '2016-12-28'
    AND COALESCE(eir.source_record->>'forumid', '') <> ''
),new_related_link AS (
    INSERT INTO shows_relatedlink (
        title,
        description,
        url,
        author,
        error,
        content_id,
        type_id
    ) SELECT
        ofc.oldforum_title, -- title
        CONCAT('Forum discussion for ', ofc.new_content_title), -- description
        ofc.forum_url, -- url
        '', --author
        false, -- error
        ofc.new_content_id, -- content_id
        2 -- type_id for forum discussion
    FROM old_forum_connections AS ofc
    RETURNING id
)
UPDATE podcasts_podcastepisode
SET comments = ofc.forum_url
FROM old_forum_connections AS ofc
WHERE podcasts_podcastepisode.id = ofc.podcast_episode_id
;

-- Populate known links for new forum
WITH new_forum_connections AS (
    SELECT
        trim(COALESCE(NULLIF(nf.title,''), sc.title)) AS newforum_title,
        trim(sc.title) AS new_content_title,
        CONCAT(
            'https://community.frontrowcrew.com/t/',
            eir.source_record->>'forumid',
            '/'
        ) AS forum_url,
        eir.new_id AS new_content_id,
        pe.id AS podcast_episode_id
    FROM etl_importrecord AS eir
    LEFT JOIN frc_etl.newforum AS nf
        ON nf.id = (eir.source_record->>'forumid')::int
    JOIN shows_content AS sc
        ON eir.new_id = sc.id
    LEFT JOIN podcasts_podcastepisode AS pe
        ON pe.id = sc.podcast_episode_id
    WHERE eir.old_table_name in ('podcast_episode', 'videos_video')
    AND eir.new_table_name = 'shows_content'
    AND sc.pub_time > '2016-12-27'
    AND COALESCE(eir.source_record->>'forumid', '') <> ''
), new_related_link AS (
    INSERT INTO shows_relatedlink (
        title,
        description,
        url,
        author,
        error,
        content_id,
        type_id
    ) SELECT
        nfc.newforum_title, -- title
        CONCAT('Forum discussion for ', nfc.new_content_title), -- description
        nfc.forum_url, -- url
        '', --author
        false, -- error
        nfc.new_content_id, -- content_id
        2 -- type_id for forum discussion
    FROM new_forum_connections AS nfc
    RETURNING id
)
UPDATE podcasts_podcastepisode
SET comments = nfc.forum_url
FROM new_forum_connections AS nfc
WHERE podcasts_podcastepisode.id = nfc.podcast_episode_id
;
