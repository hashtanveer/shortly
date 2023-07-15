from account.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, ShortLink

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=ShortLink)
def increment_user_count(sender, instance, created, **kwargs):
    if created:
        instance.profile.increment_shorturls_count()