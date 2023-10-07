-- Turn videos into content
WITH video_show_map AS (
    SELECT
        old_id,
        new_id
    FROM
        etl_importrecord
    WHERE
        old_table_name = 'videos_show'
), old_videos_video AS (
    SELECT
        nextval('shows_content_id_seq') AS new_id,
        vv.id AS old_id,
        trim(vv.title) AS title,
        trim(vv.slug) AS slug,
        (vv.pub_date + interval '20 hours') AT TIME ZONE 'America/New_York' AS pub_date,
        vsm.new_id AS show_id,
        trim(vv.description) AS description,
        trim(vv._description_rendered) AS rendered_description,
        vv.video_id AS video_id
    FROM frc_etl.videos_video AS vv
    JOIN video_show_map AS vsm
        ON vv.show_id = vsm.old_id
), new_video_content AS (
    INSERT INTO public.shows_content (
        id,
        is_published,
        pub_time,
        title,
        show_id,
        slug,
        catalog_number,
        image,
        image_description,
        creation_time,
        last_modified_time,
        rendered_html,
        original_content,
        content_format
    ) SELECT
        ovv.new_id, -- id
        TRUE, --is_published
        ovv.pub_date, --pub_time
        ovv.title, -- title
        ovv.show_id, -- show_id
        ovv.slug, -- slug
        ovv.old_id, -- catalog_number
        '', -- image
        CONCAT('YouTube thumbnail for ', ovv.title), -- image_description
        ovv.pub_date, -- creation_time
        CURRENT_TIMESTAMP, -- last_modified_time
        ovv.rendered_description, -- rendered_html
        ovv.description, -- original_content
        'HTML' -- content_format
    FROM old_videos_video AS ovv
    RETURNING id
), embedded_video AS (
    INSERT INTO public.embeds_media (
        id,
        description,
        media_id,
        service_id
    ) SELECT
        nextval('embeds_media_id_seq') AS id, -- ID
        ovv.title, -- description
        ovv.video_id, -- YouTube ID
        1 -- YOUTUBE
    FROM old_videos_video AS ovv
    RETURNING id, media_id
), embedded_video_relation AS (
    INSERT INTO public.shows_content_embedded_media (
        content_id,
        media_id
    ) SELECT
        ovv.new_id, -- New content id
        ev.id -- embedded media id
    FROM embedded_video AS ev
    JOIN old_videos_video AS ovv
        ON ev.media_id = ovv.video_id
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
    ovv.old_id,
    'videos_video',
    ovv.new_id,
    'shows_content',
    row_to_json(vv)
FROM old_videos_video AS ovv
LEFT JOIN frc_etl.videos_video as vv
ON ovv.old_id = vv.id
;
