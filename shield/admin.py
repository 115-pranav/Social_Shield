from django.contrib import admin

from .models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "category",
        "risk_level",
        "confidence",
        "created_at",
    )

    list_filter = (
        "category",
        "risk_level",
    )

    search_fields = (
        "message",
    )

    ordering = (
        "-created_at",
    )