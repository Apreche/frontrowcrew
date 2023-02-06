-- Turn news into content
WITH old_news AS (
    SELECT
        nextval('shows_content_id_seq') AS new_id,
        nn.id AS old_id,
        nn.title AS title,
        nn.slug AS slug,
        nn.pub_date AS pub_date,
        nn.body AS body,
        nn._body_rendered AS body_rendered
    FROM frc_etl.news_news AS nn
), news_show AS (
    SELECT
        id
    FROM public.shows_show
    WHERE slug='news'
),
new_news AS (
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
        image,
        image_description
    ) SELECT
        odn.new_id,
        odn.title,
        odn.slug,
        odn.old_id, -- old id is catalog_number
        odn.pub_date, -- creation_time
        CURRENT_TIMESTAMP, -- last_modified_time
        odn.pub_date, -- pub_time
        TRUE, -- is_published
        odn.body_rendered, -- rendered_html
        odn.body, -- original_content
        'HTML', --content_format
        ns.id, -- show_id
        '', -- image
        '' -- image_description
    FROM old_news AS odn
    CROSS JOIN news_show AS ns
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
    odn.old_id,
    'news_news',
    odn.new_id,
    'shows_content',
    row_to_json(nn)
FROM old_news AS odn
LEFT JOIN frc_etl.news_news AS nn
ON odn.old_id = nn.id
;
