from django.db import models
from django.contrib.auth.models import User


class Analysis(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    message = models.TextField()

    category = models.CharField(
        max_length=30
    )

    risk_level = models.CharField(
        max_length=20
    )

    confidence = models.FloatField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.category} - {self.risk_level}"