import crispy_forms
import magic

from crispy_forms import layout as crispy_layout
from crispy_forms import bootstrap
from crispy_bootstrap5 import bootstrap5
from django import forms, urls
from django.core import exceptions
from django.utils import timezone
from pagedown.widgets import PagedownWidget
from betafrontrowcrew import utils

from creator import models
from media import models as media_models
from shows import models as show_models
from podcasts import models as podcast_models


class MP3UploadForm(forms.ModelForm):

    class Meta:
        model = media_models.MP3
        fields = ("file",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = crispy_forms.helper.FormHelper()
        self.helper.include_media = False
        self.helper.form_method = "post"
        self.helper.form_id = "mp3dropzone"
        self.helper.form_class = "dropzone"
        self.helper.form_action = urls.reverse("creator-upload")
        self.helper.layout = crispy_layout.Layout(
            crispy_layout.Field("file", type="hidden")
        )

    def clean_file(self):
        file = self.cleaned_data.get("file", False)
        filetype = magic.from_buffer(file.read(2048))
        file.seek(0)  # TODO: Is this necessary?
        if not filetype.startswith(
            "Audio file with ID3"
        ):
            raise exceptions.ValidationError(
                "Uploaded file is not an audio file with ID3"
            )
        return file


class PodcastCreatorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.include_media = False
        self.helper.layout = crispy_forms.layout.Layout(
            bootstrap5.FloatingField("destination"),
            bootstrap5.FloatingField("show"),
            bootstrap5.FloatingField("catalog_number"),
            bootstrap5.FloatingField("pub_time"),
            bootstrap5.FloatingField("title"),
            bootstrap5.FloatingField("tags"),
            bootstrap5.FloatingField("description"),
            bootstrap5.Field("body"),
            crispy_layout.HTML("<hr />"),
            bootstrap5.BS5Accordion(
                bootstrap.AccordionGroup(
                    "Advanced Podcast Fields",
                    bootstrap5.FloatingField("author_name"),
                    bootstrap5.FloatingField("author_email"),
                    bootstrap5.Field("image"),
                    bootstrap5.FloatingField("image_description"),
                    bootstrap5.FloatingField("itunes_title"),
                    bootstrap5.Field("itunes_image"),
                    bootstrap5.FloatingField("itunes_image_description"),
                    bootstrap5.FloatingField("itunes_explicit"),
                    bootstrap5.FloatingField("itunes_episode_type"),
                    bootstrap5.FloatingField("itunes_season_number"),
                    bootstrap5.FloatingField("itunes_episode_number"),
                    bootstrap5.Field("itunes_block"),
                    active=False,
                ),
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        show = cleaned_data.get("show")
        catalog_number = cleaned_data.get("catalog_number")
        conflicting_content = show_models.Content.objects.filter(
            show=show,
            catalog_number=catalog_number,
        )
        if conflicting_content:
            raise exceptions.ValidationError(
                f"There is already content for {show} with catalog number {catalog_number}"
            )

    destination = forms.ModelChoiceField(
        label="FTP Destination",
        queryset=media_models.FTPDestination.objects.all(),
    )
    show = forms.ModelChoiceField(
        label="Show",
        queryset=show_models.Show.objects.all(),
    )

    def clean_show(self):
        if self.cleaned_data["show"].podcast is None:
            raise exceptions.ValidationError(
                "Selected show must be a podcast."
            )
        return self.cleaned_data["show"]

    title = forms.CharField(
        label="Episode Title",
    )
    catalog_number = forms.CharField(
        label="Catalog Number",
        initial=timezone.localtime(
            timezone.now()
        ).strftime("%Y%m%d")
    )
    pub_time = utils.forms.DateTimeLocalField(
        label="Publication Time",
        initial=timezone.localtime(
            timezone.now()
        )
    )
    tags = forms.CharField(
        label="Tags",
        required=False,
    )
    description = forms.CharField(
        label="Short Description",
        widget=forms.widgets.Textarea(),
    )
    body = forms.CharField(
        label="Full Web Content",
        widget=PagedownWidget(),
    )

    # Optional Podcast Fields
    author_name = forms.CharField(
        label="Author Name",
        required=False,
    )
    author_email = forms.EmailField(
        label="Author Email",
        required=False,
    )
    image = forms.FileField(
        label="Image",
        required=False,
    )
    image_description = forms.CharField(
        label="Image Description",
        required=False,
    )
    itunes_title = forms.CharField(
        label="iTunes Alternate Title",
        required=False,
    )
    itunes_image = forms.FileField(
        label="iTunes Image",
        required=False,
    )
    itunes_image_description = forms.CharField(
        label="iTunes Image Description",
        required=False,
    )
    itunes_episode_number = forms.IntegerField(
        label="iTunes Episode Number",
        required=False,
    )
    itunes_season_number = forms.IntegerField(
        label="iTunes Season Number",
        required=False,
    )
    itunes_explicit = forms.NullBooleanField(
        label="iTunes Explicit",
        required=False,
    )
    itunes_episode_type = forms.ChoiceField(
        label="iTunes Episode Type",
        required=False,
        choices=podcast_models.PodcastEpisode.EpisodeType.choices,
    )
    itunes_block = forms.BooleanField(
        label="iTunes Block",
        required=False,
    )


class RelatedLinkForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.include_media = False
        self.helper.layout = crispy_forms.layout.Layout(
            crispy_layout.Div(
                bootstrap5.FloatingField("title", wrapper_class="col"),
                bootstrap5.FloatingField("url", wrapper_class="col"),
                bootstrap5.FloatingField("author", wrapper_class="col"),
                css_class="row",
            ),
            crispy_layout.Div(
                bootstrap5.FloatingField("description"),
                css_class="row",
            ),
            crispy_layout.HTML("<hr />"),
        )
        self.helper.label_class = "ps-4"

    title = forms.CharField(
        label="Title",
    )
    url = forms.URLField(
        label="URL",
    )
    author = forms.CharField(
        label="Author",
    )
    description = forms.CharField(
        label="Description",
        widget=forms.widgets.Textarea(),
        required=False,
    )


class ChapterForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = crispy_forms.helper.FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.include_media = False
        self.helper.layout = crispy_forms.layout.Layout(
            crispy_layout.Div(
                bootstrap5.FloatingField("start_time", wrapper_class="col"),
                bootstrap5.FloatingField("title", wrapper_class="col"),
                css_class="row",
            ),
            bootstrap5.BS5Accordion(
                bootstrap.AccordionGroup(
                    "Extra Chapter Data",
                    bootstrap5.FloatingField("description"),
                    bootstrap5.FloatingField("url"),
                    bootstrap5.FloatingField("url_description"),
                    bootstrap5.Field("image"),
                    bootstrap5.FloatingField("image_description"),
                    active=False,
                ),
            ),
            crispy_layout.HTML("<hr />"),
        )
        self.helper.label_class = "ps-4"

    start_time = forms.IntegerField(
        label="Start Time",
    )
    title = forms.CharField(
        label="Title",
    )
    description = forms.CharField(
        label="Description",
        widget=forms.widgets.Textarea(),
        required=False,
    )
    url = forms.URLField(
        label="URL",
        required=False,
    )
    url_description = forms.CharField(
        label="URL Description",
        widget=forms.widgets.Textarea(),
        required=False,
    )
    image = forms.FileField(
        label="Image",
        required=False,
    )
    image_description = forms.CharField(
        label="Image Description",
        widget=forms.widgets.Textarea(),
        required=False,
    )
