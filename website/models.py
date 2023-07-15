from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password 
from django.contrib.auth.hashers import check_password as _check_password

User = get_user_model()

def get_guest_user():
    return User.objects.filter(name=settings.GUEST_USERNAME).first().id

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    _shorturls_count_today = models.PositiveIntegerField(default=0)
    last_reset = models.DateTimeField(auto_now_add=True)
    premium_till = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name

    def can_make_shortlink(self):
        #Always allow Guest User
        if self.shorturls_allowed == -1:
            return True
        if self.last_reset.date() < timezone.now().date():
            self.reset_shorturls()
        return self.shorturls_count_today < self.shorturls_allowed

    def set_premium(self):
        self.premium_till = timezone.now() + timezone.timedelta(days=30)
        self.save()

    @property
    def premium(self):
        if self.premium_till and self.premium_till < timezone.now():
            # Premium subscription has expired, return False
            return False
        return True

    @property
    def shorturls_allowed(self):
        if self.user.id == get_guest_user():
            return -1
        
        return settings.SHORTURLS_ALLOWED_PREMIUM if self.premium else settings.SHORTURLS_ALLOWED_FREE

    @property
    def shorturls_count_today(self):
        if self.last_reset.date() < timezone.now().date():
            self.reset_shorturls()
        return self._shorturls_count_today

    @property
    def remaining_shorturls(self):
        remaining = self.shorturls_allowed - self.shorturls_count_today
        return max(remaining, 0)
    
    @property
    def total_shorturls(self):
        return ShortLink.objects.filter(profile=self).count()

    def increment_shorturls_count(self):
        self._shorturls_count_today += 1
        self.save()

    def reset_shorturls(self):
        self._shorturls_count_today = 0
        self.last_reset = timezone.now()
        self.save()

def get_guest_profile():
    guest_user = User.objects.filter(name='Guest').first()
    return Profile.objects.get(user=guest_user).id

class ShortLink(models.Model):
    profile = models.ForeignKey(Profile, default=get_guest_profile, on_delete=models.CASCADE)
    code = models.CharField(max_length=20,unique=True)
    url = models.URLField(max_length=settings.MAX_URL_LENGTH ,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    password_protected = models.BooleanField(default=False)
    password = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self) -> str:
        return self.code
    
    def save(self, *args, **kwargs):
        if self.password and not self.password_protected:
            self.password = None

        if self.password_protected and self.password:
            self.password = make_password(self.password)
        
        super().save(*args, **kwargs)


    def check_password(self, input_password):
        return _check_password(input_password, self.password)
    
    def set_password(self, password):
        self.password_protected = True
        self.password = make_password(password)
        self.save(using=self._db)
    
    def remove_password(self):
        self.password_protected = False
        self.password = None
        self.save()