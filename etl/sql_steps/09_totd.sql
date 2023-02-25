WITH episode_id_map AS (
    SELECT
        old_id AS episode_id,
        new_id AS content_id
    FROM etl_importrecord
    WHERE
        old_table_name = 'podcast_episode'
    AND
        new_table_name = 'shows_content'

), old_totd AS (
    SELECT
        nextval('shows_relatedlink_id_seq') AS related_link_id,
        tt.id AS old_id,
        trim(tt.title) AS title,
        trim(tt.url) AS url,
        trim(tt.author) AS author,
        tt.episode_id AS episode_id,
        eim.content_id AS content_id,
        tt.error::int::boolean AS error
    FROM frc_etl.things_thing AS tt
    JOIN episode_id_map AS eim
        ON eim.episode_id = tt.episode_id
), new_related_link AS (
    INSERT INTO shows_relatedlink (
        id,
        title,
        description,
        url,
        author,
        error,
        content_id,
        type_id
    ) SELECT
        ot.related_link_id, -- id
        ot.title,
        '', -- description
        ot.url,
        ot.author,
        ot.error,
        ot.content_id,
        1 -- type_id
    FROM old_totd AS ot
    RETURNING id
)
INSERT INTO public.etl_importrecord (
    import_time,
    old_id,
    old_table_name,
    new_id,
    new_table_name,
    source_record
) SELECT
    CURRENT_TIMESTAMP,
    ot.old_id, -- old_id
    'things_thing', -- old_table_name
    ot.related_link_id, -- new_id
    'shows_relatedlink', --new_table_name
    row_to_json(tt)
FROM old_totd AS ot
LEFT JOIN frc_etl.things_thing AS tt
ON ot.old_id = tt.id
;
