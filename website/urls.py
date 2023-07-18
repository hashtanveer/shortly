from django.urls import path
from .views import HomePageView, LoginPageView, SignupView, CreateShortLinkView, ListShortLinkView, ShortLinkView

app_name = "website"

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='register'),
    path('shortlink/create', CreateShortLinkView.as_view(), name='create'),
    path('shortlink/list', ListShortLinkView.as_view()),
    path('<code>/', ShortLinkView.as_view()),
]