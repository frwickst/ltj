from django.contrib import admin

from .models import ShpImport


@admin.register(ShpImport)
class ShpImportAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by', 'created_time')
    actions = None

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.save()
