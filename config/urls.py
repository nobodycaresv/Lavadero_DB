from django.contrib import admin
from django.urls import include, path
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]
if hasattr(core_views, "home"):
    urlpatterns.append(path("", core_views.home, name="home"))