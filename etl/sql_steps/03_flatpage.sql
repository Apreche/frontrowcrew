-- Import flatpages directly
INSERT INTO django_flatpage (
    url,
    title,
    content,
    enable_comments,
    template_name,
    registration_required
)
SELECT
    trim(url),
    trim(title),
    trim(content),
    enable_comments::int::bool,
    trim(template_name),
    registration_required::int::bool
FROM frc_etl.django_flatpage;

INSERT into django_flatpage_sites (
    flatpage_id,
    site_id
)
SELECT
    dfp.id,
    1 -- Only one site
FROM django_flatpage as dfp;
