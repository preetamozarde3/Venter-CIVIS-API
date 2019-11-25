from django.contrib import admin
import os

from Venter.models import Category, File, Organisation, Draft, UserResponse, SentenceCategory

class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('organisation_name',)

class DraftAdmin(admin.ModelAdmin):
    # list_display = ('draft_name', 'ml_output_filename')
    list_display = ('draft_name',)
    list_filter = ['organisation_name', 'creation_date']

    # def ml_output_filename(self, obj):
    #     return os.path.basename(obj.ml_output.output_file_json.name)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category',)
    list_filter = ['draft_name']

class SentenceCategoryAdmin(admin.ModelAdmin):
    list_display = ('category',)
    list_filter = ['draft_name']

class FileAdmin(admin.ModelAdmin):
    list_display = ('ckpt_date',)
    list_filter = ['organisation_name', 'ckpt_date']

class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('user_response', 'creation_date',)
    list_filter = ['draft_name', 'creation_date']


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Draft, DraftAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SentenceCategory, SentenceCategoryAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(UserResponse, UserResponseAdmin)