from rest_framework import serializers
from django.conf import settings
from .models import ShortLink

class ShortLinkSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%B %d, %Y, %I:%M %p")
    class Meta:
        model = ShortLink
        fields = ['code', 'created_at', 'password_protected', 'url']