import http
from django import forms
from django import http as django_http
from django import shortcuts
from django import urls
from django.views.decorators import http as view_http_decorators
from django.views.decorators import vary as vary_decorators
from django.contrib.auth import decorators as auth_decorators
from betafrontrowcrew import utils
from media import models as media_models

from . import forms as creator_forms
from . import models


@auth_decorators.login_required
@vary_decorators.vary_on_headers("Accept")
def upload(request):
    """ A view to handle uploading of the MP3 prior to episode creation """

    template_name = "creator/upload_form.html"
    upload_form = creator_forms.MP3UploadForm()
    # Handle file uploads
    if request.method == "POST":
        upload_form = creator_forms.MP3UploadForm(
            request.POST, request.FILES
        )
        if upload_form.is_valid():
            # Successful upload
            uploaded_mp3 = upload_form.save()
            # Handle different response formats
            success_redirect_url = urls.reverse(
                "creator-podcast-episode",
                kwargs={"mp3_id": uploaded_mp3.id}
            )
            if request.accepts("application/json"):
                # If JSON, send redirect URL in response
                return django_http.JsonResponse(
                    {"redirect_url": success_redirect_url}
                )
            else:
                # If HTML, send actual redirect
                return shortcuts.redirect(success_redirect_url)
        else:
            # Failed upload JSON
            if request.accepts("application/json"):
                # If JSON Failure, send errors in JSON format
                return django_http.HttpResponseBadRequest(
                    upload_form.errors.as_json(escape_html=True),
                    content_type="application/json",
                )
            else:
                return shortcuts.render(
                    request,
                    template_name,
                    {"upload_form": upload_form},
                    status=http.BAD_REQUEST
                )
    return shortcuts.render(
        request,
        template_name,
        {"upload_form": upload_form},
    )


MAIN_FORM_PREFIX = "main"
RELATED_LINK_FORMSET_PREFIX = "totd"
CHAPTER_FORMSET_PREFIX = "chapters"


@auth_decorators.login_required
def create_podcast_episode(request, mp3_id=None):
    """ Create a podcast using the specified MP3 file """
    mp3 = shortcuts.get_object_or_404(
        media_models.MP3,
        id=mp3_id,
    )

    template_name = "creator/create_podcast_form.html"
    RelatedLinkFormset = forms.formset_factory(
        creator_forms.RelatedLinkForm,
        extra=2,
    )
    ChapterFormset = forms.formset_factory(
        creator_forms.ChapterForm,
        extra=2,
    )
    if request.method == "POST":
        main_form = creator_forms.PodcastCreatorForm(
            request.POST,
            request.FILES,
            prefix=MAIN_FORM_PREFIX,
        )
        related_link_formset = RelatedLinkFormset(
            request.POST,
            prefix=RELATED_LINK_FORMSET_PREFIX,
        )
        chapter_formset = ChapterFormset(
            request.POST,
            request.FILES,
            prefix=CHAPTER_FORMSET_PREFIX,
        )
        if all(
            [
                main_form.is_valid(),
                related_link_formset.is_valid(),
                chapter_formset.is_valid(),
            ]
        ):
            # POST Success
            episode = models.Episode.objects.create(
                mp3=mp3,
                **main_form.cleaned_data
            )

            for related_link_data in related_link_formset.cleaned_data:
                models.RelatedLink.objects.create(
                    episode=episode,
                    **related_link_data,
                )

            for chapter_data in chapter_formset.cleaned_data:
                models.Chapter.objects.create(
                    episode=episode,
                    **chapter_data,
                )

            template_name = "creator/create_podcast_success.html"
            context = {
                "episode": episode,
            }
            return shortcuts.render(
                request,
                template_name,
                context,
                status=http.HTTPStatus.CREATED
            )
        else:
            # POST Failure
            context = {
                "form": main_form,
                "mp3": mp3,
                "related_link_formset": related_link_formset,
                "chapter_formset": chapter_formset,
            }
            return shortcuts.render(
                request,
                template_name,
                context,
                status=http.HTTPStatus.BAD_REQUEST
            )

    # GET
    initial_ftp_destination = None
    ftp_destinations = media_models.FTPDestination.objects.all()
    if ftp_destinations:
        initial_ftp_destination = ftp_destinations.first().id
    main_form = creator_forms.PodcastCreatorForm(
        prefix=MAIN_FORM_PREFIX,
        initial={
            "ftp_destination": initial_ftp_destination,
        }
    )

    related_link_formset = RelatedLinkFormset(
        prefix=RELATED_LINK_FORMSET_PREFIX,
    )
    initial_chapters = mp3.get_xmp_chapters() or []
    chapter_formset = ChapterFormset(
        prefix=CHAPTER_FORMSET_PREFIX,
        initial=initial_chapters,
    )

    context = {
        "form": main_form,
        "mp3": mp3,
        "related_link_formset": related_link_formset,
        "chapter_formset": chapter_formset,
    }
    return shortcuts.render(request, template_name, context)
