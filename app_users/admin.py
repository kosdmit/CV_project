from django.contrib import admin

from .models import Profile, SocialLinks

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birthday_date', 'gender', 'phone_number')

admin.site.register(Profile, ProfileAdmin)


class SocialLinksAdmin(admin.ModelAdmin):
    list_display = ('user', 'twitter', 'facebook', 'linked_in', 'vk', 'instagram',
                    'hh', 'git_hub')

admin.site.register(SocialLinks, SocialLinksAdmin)
