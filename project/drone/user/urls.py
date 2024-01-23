from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'user'

urlpatterns = [
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("signout/", views.signout, name="signout"),
    path("settings/", views.settings, name="settings"),
    path("settings/edit_profile/", views.edit_profile, name="edit_profile"),
    path("users/", views.all_user_page, name="all_user_page"),
    path("view_profile/<str:username>", views.view_profile, name="view_profile"),
] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)