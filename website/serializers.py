from rest_framework import serializers
from django.conf import settings
from .models import ShortLink

class ShortLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortLink
        fields = ['code', 'created_at', 'password_protected']