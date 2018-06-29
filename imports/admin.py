from django.contrib import admin
from django.db import transaction

from .models import ShpImport
from .importers import ShapefileImporter


@admin.register(ShpImport)
class ShpImportAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by', 'created_time')
    actions = None

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # only do imports when creating new instances
            ShapefileImporter.import_features(obj.shapefiles)
            obj.created_by = request.user
        obj.save()
