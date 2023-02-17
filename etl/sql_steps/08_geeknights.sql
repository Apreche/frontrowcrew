-- Load actual podcast episodes
WITH old_podcast_episodes AS (
    SELECT
        nextval('podcasts_podcastenclosure_id_seq') AS new_podcast_enclosure_id,
        nextval('podcasts_podcastepisode_id_seq') AS new_podcast_episode_id,
        nextval('shows_content_id_seq') AS new_content_id,
        op.id AS old_podcast_episode_id,
        op.title AS title,
        op.slug AS slug,
        (op.pub_date + interval '1' day) at time zone 'utc' AS pub_date,
        op.showid AS catalog_number,
        op.show_id AS show_id,
        op.body AS original_content,
        op._body_rendered AS rendered_content,
        op.mp3url AS mp3url,
        op.mp3size AS mp3size,
        show.podcast_id AS podcast_id
    FROM frc_etl.podcast_episode AS op
    JOIN public.shows_show AS show
        ON op.show_id = show.id
), podcast_enclosure AS (
    INSERT INTO public.podcasts_podcastenclosure (
        id,
        url,
        length,
        type
    ) SELECT
        op.new_podcast_enclosure_id,
        op.mp3url,
        op.mp3size,
        'audio/mpeg'
    FROM old_podcast_episodes AS op
    RETURNING id
), podcast_episode AS (
    INSERT INTO public.podcasts_podcastepisode (
        id,
        title,
        guid,
        guid_is_permalink,
        pub_date,
        description,
        duration,
        author_name,
        author_email,
        comments,
        itunes_image,
        itunes_explicit,
        itunes_title,
        itunes_episode_type,
        itunes_block,
        enclosure_id,
        podcast_id,
        image,
        image_description
    ) SELECT
        op.new_podcast_episode_id, -- id
        op.title, -- title
        CONCAT('http://frontrowcrew.com/geeknights/', op.catalog_number, '/', op.slug, '/'), -- guid
        TRUE, -- guid_is_permalink
        op.pub_date, -- pub_date
        op.rendered_content, -- description
        NULL, -- duration
        'Rym and Scott', -- author_name
        'geeknights@frontrowcrew.com', -- author_email
        '', -- comments
        '', -- itunes_image
        TRUE, -- itunes_explicit
        op.title, -- itunes_title
        '', -- itunes_episode_type
        FALSE, -- itunes_block
        op.new_podcast_enclosure_id, --enclosure_id
        op.podcast_id, -- podcast_id
        '', -- image
        '' image_description
    FROM old_podcast_episodes AS op
    RETURNING id
), new_podcast_content AS (
    INSERT INTO public.shows_content (
        id,
        title,
        slug,
        catalog_number,
        creation_time,
        last_modified_time,
        pub_time,
        is_published,
        rendered_html,
        original_content,
        content_format,
        show_id,
        podcast_episode_id,
        image,
        image_description
    ) SELECT
        op.new_content_id, -- id
        op.title, -- title
        op.slug, -- slug
        op.catalog_number, --catalog_number
        op.pub_date, -- creation_time
        CURRENT_TIMESTAMP, -- last_modified_time
        op.pub_date, -- pub_time
        TRUE, -- is_published
        op.rendered_content, -- rendered_html
        op.original_content, -- original_content
        'HTML', --content_format
        op.show_id, --show_id
        op.new_podcast_episode_id, -- podcast_episode_id
        '', --image
        '' -- image_description
    FROM old_podcast_episodes AS op
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
    op.old_podcast_episode_id,
    'podcast_episode',
    op.new_content_id,
    'shows_content',
    row_to_json(ope)
FROM old_podcast_episodes AS op
LEFT JOIN frc_etl.podcast_episode AS ope
ON op.old_podcast_episode_id = ope.id
;
