-- connect the book club announcement content to the book club episode content
WITH irec_book AS (
    SELECT
        new_id AS new_book_id,
        (source_record->>'episode_id')::bigint AS old_episode_id
    FROM etl_importrecord
    WHERE old_table_name = 'bookclub_book'
    AND new_table_name = 'shows_content'
), irec_episode AS (
    SELECT
        new_id AS new_episode_id,
        old_id AS old_episode_id
    FROM etl_importrecord
    WHERE old_table_name = 'podcast_episode'
    AND new_table_name = 'shows_content'
), content_relation AS (
    SELECT
        ib.new_book_id AS new_book_id,
        ie.new_episode_id AS new_episode_id
    FROM irec_book AS ib
    JOIN irec_episode ie
    ON ie.old_episode_id = ib.old_episode_id
), forward_relation AS (
    INSERT INTO shows_content_related_content (
        from_content_id,
        to_content_id
    ) SELECT
        cr.new_book_id,
        cr.new_episode_id
    FROM content_relation AS cr
)
-- reverse_relation for symmetry
INSERT INTO shows_content_related_content (
    from_content_id,
    to_content_id
) SELECT
    cr.new_episode_id,
    cr.new_book_id
FROM content_relation AS cr
;
