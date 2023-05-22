from django.contrib import admin

from app_social.models import Comment

# Register your models here.
class CommentAdmin(admin.ModelAdmin):
    list_display_links = ('message',)
    list_display = ('user', 'message', 'updated_date', 'is_approved')

admin.site.register(Comment, CommentAdmin)