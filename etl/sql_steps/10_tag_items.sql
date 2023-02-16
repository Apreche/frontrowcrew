WITH old_tagged_item AS (
    SELECT
        nextval('taggit_taggeditem_id_seq') AS new_id,
        tti.id AS old_id,

        etit.new_id AS new_tag_id,
        tti.tag_id AS old_tag_id,

        etio.new_id AS new_object_id,
        tti.object_id AS old_object_id,

        36 AS new_content_type_id, -- shows_content
        tti.content_type_id AS old_content_type_id
    FROM frc_etl.taggit_taggeditem AS tti
    JOIN (VALUES
        (1, 'bookclub_book'),
        (2, 'news_news'),
        (4, 'podcast_episode'),
        (7, 'videos_video')
    ) AS ctm (content_type_id, old_table_name)
        ON ctm.content_type_id = tti.content_type_id
    JOIN etl_importrecord AS etio -- for finding object_ids
        ON etio.old_table_name = ctm.old_table_name
        AND etio.old_id = tti.object_id
    JOIN etl_importrecord AS etit -- for finding tag ids
        ON etit.old_table_name = 'taggit_tag'
        AND etit.old_id = tti.tag_id
), new_tagged_item AS (
    INSERT INTO public.taggit_taggeditem (
        id,
        object_id,
        content_type_id,
        tag_id
    ) SELECT
        oti.new_id, -- id
        oti.new_object_id, --object_id
        oti.new_content_type_id, --content_type_id
        oti.new_tag_id --tag_id
    FROM old_tagged_item AS oti
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
    oti.old_id,
    'taggit_taggeditem',
    oti.new_id,
    'taggit_taggeditem',
    row_to_json(ti)
FROM old_tagged_item AS oti
LEFT JOIN frc_etl.taggit_taggeditem AS ti
ON ti.id = oti.old_id
;
