from django import forms
from django.contrib import admin
from django.utils.html import format_html

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import CameraStation, CameraCapture, CaptureDetection, SpeciesLabel


# =================== Species Labels =====================
@admin.register(SpeciesLabel)
class SpeciesLabelAdmin(admin.ModelAdmin):
    list_display = ('ClassId', 'Name', 'Description')
    ordering = ('ClassId',)
    search_fields = ('Name',)


# =================== Camera Station =====================
class CameraStationResource(resources.ModelResource):
    class Meta:
        model = CameraStation


@admin.register(CameraStation)
class CameraStationAdmin(ImportExportModelAdmin):
    resource_class = CameraStationResource

    def DateCreatedFormat(self, obj):
        return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
    DateCreatedFormat.admin_order_field = 'DateCreate'
    DateCreatedFormat.short_description = 'Date Create'

    list_display = (
        'id',
        'StationName',
        'Latitude',
        'Longitude',
        'Altitude',
        'Status',
        'DateCreatedFormat',
    )
    search_fields = ('StationName', 'Description')
    list_filter = ('Status',)


# =================== Camera Capture =====================
class CaptureDetectionInlineForm(forms.ModelForm):
    class Meta:
        model = CaptureDetection
        fields = ('Species', 'Count')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', '— select —')] + [
            (sl.Name, f'{sl.ClassId} — {sl.Name}')
            for sl in SpeciesLabel.objects.all()
        ]
        self.fields['Species'].widget = forms.Select(
            choices=choices,
            attrs={'style': 'min-width:200px;'},
        )
        self.fields['Count'].widget.attrs.update({'style': 'width:80px;'})


class CaptureDetectionInline(admin.TabularInline):
    model = CaptureDetection
    form = CaptureDetectionInlineForm
    fields = ('Species', 'Count')
    extra = 1
    min_num = 0


class CameraCaptureResource(resources.ModelResource):
    class Meta:
        model = CameraCapture
        exclude = ('Image',)


@admin.register(CameraCapture)
class CameraCaptureAdmin(ImportExportModelAdmin):
    resource_class = CameraCaptureResource
    inlines = [CaptureDetectionInline]

    def thumbnail(self, obj):
        if obj.Image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;" />', obj.Image.url)
        return '—'
    thumbnail.short_description = 'Image'

    def detections_summary(self, obj):
        parts = [f'{d.Species} ×{d.Count}' for d in obj.detections.all()]
        return ', '.join(parts) if parts else '—'
    detections_summary.short_description = 'Detections'

    list_display = (
        'id',
        'thumbnail',
        'Station',
        'DateCapture',
        'detections_summary',
        'Temperature',
        'Humidity',
        'VoltageBattery',
    )
    search_fields = ('Station__StationName', 'detections__Species')
    list_filter = ('Station', 'DateCapture')
    date_hierarchy = 'DateCapture'
    readonly_fields = ('thumbnail',)
