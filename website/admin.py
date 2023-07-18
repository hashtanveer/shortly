from django.contrib import admin
from .models import Profile, ShortLink

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id' , 'user', 'total_shorturls', 'premium', 'created_today', 'premium_till')

    def created_today(self, profile):
        shorturls_allowed = "♾️" if profile.shorturls_allowed == -1 else profile.shorturls_allowed
        return f"{profile.shorturls_count_today} / {shorturls_allowed}"

class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('code', 'profile', 'password_protected', 'url')
    search_fields = ('code', 'url')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(ShortLink, ShortLinkAdmin)