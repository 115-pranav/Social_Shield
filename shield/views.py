from pathlib import Path
import csv
import re

import joblib
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .models import Analysis

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "ML" / "model" / "social_shield_model.pkl"
model = joblib.load(MODEL_PATH)


def home(request):
    return render(request, "shield/home.html")


def analyze_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

    message = request.POST.get("message", "").strip()
    if not message:
        return JsonResponse({"error": "Please enter a message."}, status=400)

    prediction = model.predict([message])[0]
    probabilities = model.predict_proba([message])[0]
    confidence = round(max(probabilities) * 100, 2)

    risk_levels = {
        "Safe": "LOW",
        "Spam": "HIGH",
        "Phishing": "CRITICAL",
        "Suspicious": "MEDIUM",
        "Abusive": "HIGH",
    }
    risk = risk_levels.get(prediction, "UNKNOWN")

    has_url = bool(re.search(r"https?://\S+|www\.\S+", message, re.IGNORECASE))

    Analysis.objects.create(
        user=request.user if request.user.is_authenticated else None,
        message=message,
        category=prediction,
        risk_level=risk,
        confidence=confidence,
    )

    return JsonResponse({
        "category": prediction,
        "risk": risk,
        "confidence": confidence,
        "has_url": has_url,
    })


def history(request):
    if not request.user.is_authenticated:
        return redirect("login")

    analyses = Analysis.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "shield/history.html", {"analyses": analyses})


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    user_analyses = Analysis.objects.filter(user=request.user)

    context = {
        "total": user_analyses.count(),
        "safe": user_analyses.filter(category="Safe").count(),
        "spam": user_analyses.filter(category="Spam").count(),
        "phishing": user_analyses.filter(category="Phishing").count(),
        "suspicious": user_analyses.filter(category="Suspicious").count(),
        "abusive": user_analyses.filter(category="Abusive").count(),
        "recent": user_analyses.order_by("-created_at")[:10],
    }

    return render(request, "shield/dashboard.html", context)


def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            return render(request, "shield/register.html",
                          {"error": "Please fill in all fields."})

        if password != confirm_password:
            return render(request, "shield/register.html",
                          {"error": "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            return render(request, "shield/register.html",
                          {"error": "Username already exists."})

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return redirect("login")

    return render(request, "shield/register.html")


def login_user(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(
            request,
            "shield/login.html",
            {"error": "Invalid username or password."},
        )

    return render(request, "shield/login.html")


def logout_user(request):
    logout(request)
    return redirect("home")


def download_data(request):
    if not request.user.is_authenticated:
        return redirect("login")

    analyses = Analysis.objects.filter(user=request.user).order_by("-created_at")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="social_shield_my_data.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(["Date", "Message", "Category", "Risk Level", "Confidence"])

    for analysis in analyses:
        writer.writerow([
            analysis.created_at.strftime("%d-%m-%Y %H:%M"),
            analysis.message,
            analysis.category,
            analysis.risk_level,
            analysis.confidence,
        ])

    return response


def delete_my_data(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        Analysis.objects.filter(user=request.user).delete()

    return redirect("dashboard")
