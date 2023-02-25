-- ETL for shows

-- Podcasts
WITH geeknights AS (
    INSERT INTO public.shows_show (
        title,
        slug,
        logo,
        thumbnail,
        is_published,
        pub_time,
        display_in_nav,
        description
    ) VALUES (
        'GeekNights', -- title
        'geeknights', -- slug
        'show_logos/geeknights-podcast.png', -- logo
        '', -- thumbnail
        TRUE, -- is_published
        CURRENT_TIMESTAMP, -- pub_time
        TRUE, -- display_in_nav
        '' -- description
    )
    RETURNING id
), old_show AS (
    SELECT
        nextval('shows_show_id_seq') AS new_id,
        ps.id AS old_id,
        ps.title AS title,
        ps.slug AS slug,
        ps.logo AS logo,
        ps.thumbnail AS thumbnail
    FROM frc_etl.podcast_show AS ps
), sub_show AS (
    INSERT INTO public.shows_show (
        id,
        title,
        slug,
        logo,
        thumbnail,
        is_published,
        pub_time,
        display_in_nav,
        description
    ) SELECT
        new_id,
        title,
        slug,
        logo,
        thumbnail,
        TRUE, -- is_published
        CURRENT_TIMESTAMP, -- pub_time
        FALSE, -- display_in_nav
        '' -- description
    FROM old_show
    RETURNING id
), sub_show_connection AS (
    INSERT into public.shows_show_sub_shows (
        from_show_id,
        to_show_id
    ) SELECT
        geeknights.id,
        sub_show.id
    FROM sub_show
    CROSS JOIN geeknights
)
INSERT INTO public.etl_importrecord (
    import_time,
    old_id,
    old_table_name,
    new_id,
    new_table_name,
    source_record
) SELECT
    CURRENT_TIMESTAMP, -- import_time
    os.old_id,
    'podcast_show', -- old_table_name
    os.new_id,
    'shows_show', -- new_table_name
    row_to_json(ps) -- source_record
FROM old_show AS os
LEFT join frc_etl.podcast_show AS ps
ON os.old_id = ps.id
;

-- Video Shows
WITH old_video_show AS (
    SELECT
        nextval('shows_show_id_seq') AS new_id,
        vs.id AS old_id,
        vs.title AS title,
        vs.slug AS slug
    FROM frc_etl.videos_show as vs
), new_video_show AS (
    INSERT INTO public.shows_show (
        id,
        title,
        slug,
        logo,
        thumbnail,
        is_published,
        pub_time,
        display_in_nav,
        description
    ) SELECT
        ovs.new_id AS id,
        ovs.title,
        ovs.slug,
        '', -- logo
        '', -- thumbnail
        TRUE, -- is_published
        CURRENT_TIMESTAMP, -- pub_time
        FALSE, -- display_in_nav
        '' -- description
    FROM old_video_show AS ovs
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
    CURRENT_TIMESTAMP, -- import_time
    ovs.old_id,
    'videos_show', -- old_table_name
    ovs.new_id,
    'shows_show', -- new_table_name
    row_to_json(vs) -- source_record
FROM old_video_show AS ovs
LEFT join frc_etl.videos_show AS vs
ON ovs.old_id = vs.id
;

-- News show hard-coded
INSERT INTO public.shows_show (
    title,
    slug,
    logo,
    thumbnail,
    is_published,
    pub_time,
    display_in_nav,
    description
) VALUES (
    'News',
    'news',
    '',
    '',
    TRUE,
    CURRENT_TIMESTAMP,
    FALSE,
    ''
);
