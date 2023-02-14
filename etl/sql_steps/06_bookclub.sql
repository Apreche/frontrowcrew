-- Turn bookclub into content
WITH old_bookclub_books AS (
    SELECT
        nextval('shows_content_id_seq') AS new_id,
        bb.id AS old_id,
        bb.title AS title,
        bb.slug AS slug,
        bb.announce_date AS announce_date,
        bb.author AS author,
        bb.cover AS cover_image,
        bb.picker AS picker,
        bb.amazon_link AS purchase_link,
        bb.episode_id AS episode_id,
        bb.description AS description,
        bb._description_rendered AS rendered_description
    FROM frc_etl.bookclub_book AS bb
), bookclub_show AS (
    SELECT
        id
    FROM public.shows_show
    WHERE slug = 'book-club'
),
new_bookclub_books AS (
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
        obb.new_id, -- id
        TRUE, --is_published
        obb.announce_date, --pub_time
        obb.title, -- title
        bs.id, -- show_id
        obb.slug, -- slug
        obb.old_id, -- catalog_number
        obb.cover_image, -- image
        CONCAT('&ldquo;', obb.title, '&rdquo; book cover'), -- image_description
        obb.announce_date, -- creation_time
        CURRENT_TIMESTAMP, -- last_modified_time
        obb.rendered_description, -- rendered_html
        obb.description, -- original_content
        'HTML' -- content_format
    FROM old_bookclub_books AS obb
    CROSS JOIN bookclub_show AS bs
    RETURNING id
),
bookclub_book_author AS (
    INSERT INTO shows_metadata (
        id,
        data,
        content_id,
        type_id
    ) SELECT
        nextval('shows_metadata_id_seq'),
        obb.author,
        obb.new_id,
        1 -- BOOK_AUTHOR
    FROM old_bookclub_books AS obb
    RETURNING id
),
bookclub_purchase_link AS (
    INSERT INTO  shows_relatedlink (
        id,
        title,
        description,
        url,
        author,
        error,
        content_id,
        type_id
    ) SELECT
        nextval('shows_relatedlink_id_seq'),
        CONCAT('Purchase "', obb.title, '"'),
        CONCAT('&ldquo;', obb.title, '&rdquo; book purchase link.'),
        obb.purchase_link,
        '', -- AUTHOR
        FALSE, -- ERROR
        obb.new_id,
        3 -- PURCHASE_LINK
    FROM old_bookclub_books AS obb
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
    obb.old_id,
    'bookclub_book',
    obb.new_id,
    'shows_content',
    row_to_json(bb)
FROM old_bookclub_books AS obb
LEFT JOIN frc_etl.bookclub_book as bb
ON obb.old_id = bb.id
;
