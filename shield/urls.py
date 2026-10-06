from pathlib import Path

import cv2
import numpy as np
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import path

from .sitemaps import StaticViewSitemap
from . import views


sitemaps = {
    "static": StaticViewSitemap,
}


def google_verification(request):
    file_path = Path(settings.BASE_DIR) / "google909cc2a2e7f088d8.html"

    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        return HttpResponse(content, content_type="text/html")

    return HttpResponse("Verification file not found.", status=404)


def robots_txt(request):
    content = """User-agent: *
Allow: /

Sitemap: https://social-shield-ir70.onrender.com/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    path("", views.home, name="home"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("analyze/", views.analyze_message, name="analyze_message"),
    path("qr-scanner/", views.qr_scanner, name="qr_scanner"),
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

    path(
        "google909cc2a2e7f088d8.html",
        google_verification,
        name="google_verification",
    ),

    path("robots.txt", robots_txt, name="robots_txt"),
]