from django.urls import path
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap
from . import views

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("", views.home, name="home"),
    path("analyze/", views.analyze_message, name="analyze_message"),
    path("history/", views.history, name="history"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("download-data/", views.download_data, name="download_data"),
    path("delete-my-data/", views.delete_my_data, name="delete_my_data"),

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]