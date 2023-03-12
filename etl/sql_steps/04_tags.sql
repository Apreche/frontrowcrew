-- Import tags
WITH old_tags AS (
    SELECT
        nextval('taggit_tag_id_seq') AS new_id,
        tt.id AS old_id,
        tt.name AS name,
        tt.slug AS slug
    FROM frc_etl.taggit_tag AS tt
), new_tags AS (
    INSERT INTO public.taggit_tag (
        id,
        name,
        slug
    ) SELECT
        new_id,
        name,
        slug
    FROM old_tags
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
    ot.old_id,
    'taggit_tag', -- old_table_name
    ot.new_id,
    'taggit_tag', -- new_table_name
    row_to_json(tt) -- source_record
FROM old_tags AS ot
LEFT JOIN frc_etl.taggit_tag AS tt
ON ot.old_id = tt.id
;
