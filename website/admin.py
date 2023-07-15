from django.contrib import admin
from .models import Profile, ShortLink

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id' , 'user', 'total_shorturls', 'premium', 'created_today')

    def created_today(self, profile):
        shorturls_allowed = "♾️" if profile.shorturls_allowed == -1 else profile.shorturls_allowed
        return f"{profile.shorturls_count_today} / {shorturls_allowed}"

admin.site.register(Profile, ProfileAdmin)
admin.site.register(ShortLink)