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
    if request.method == "GET":
        return render(request, "shield/analyze.html")

    if request.method != "POST":
        return JsonResponse({"error": "Only GET and POST requests are allowed."}, status=405)

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

    has_url = bool(
    re.search(
        r"https?://\S+|www\.\S+",
        message,
        re.IGNORECASE
    )
)

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
# ============================================================
# APP CHECKER
# ============================================================

def app_checker(request):

    result = None

    if request.method == "POST":

        app_name = request.POST.get("app_name", "").strip()
        package_name = request.POST.get("package_name", "").strip()

        suspicious_words = [
            "hack",
            "crack",
            "mod",
            "cheat",
            "spy",
            "tracking",
            "free money",
            "unlimited"
        ]

        combined_text = (
            app_name + " " + package_name
        ).lower()

        found_words = [
            word
            for word in suspicious_words
            if word in combined_text
        ]

        if not app_name and not package_name:

            result = {
                "status": "⚠️ Input Required",
                "risk": "UNKNOWN",
                "message": "Please enter an app name or package name."
            }

        elif found_words:

            result = {
                "status": "⚠️ Suspicious",
                "risk": "MEDIUM",
                "message": (
                    "Suspicious indicators found: "
                    + ", ".join(found_words)
                )
            }

        else:

            result = {
                "status": "✅ No Basic Warning Found",
                "risk": "LOW",
                "message": (
                    "No obvious suspicious indicators "
                    "were found in the supplied app information."
                )
            }

    return render(
        request,
        "shield/app_checker.html",
        {"result": result}
    )


# ============================================================
# PHONE CHECKER
# ============================================================

def phone_checker(request):

    result = None

    if request.method == "POST":

        phone = request.POST.get("phone", "").strip()

        digits = "".join(
            character
            for character in phone
            if character.isdigit()
        )

        if not phone:

            result = {
                "status": "⚠️ Input Required",
                "risk": "UNKNOWN",
                "message": "Please enter a phone number."
            }

        elif len(digits) < 10:

            result = {
                "status": "❌ Invalid Format",
                "risk": "MEDIUM",
                "message": "The phone number appears to be too short."
            }

        elif len(digits) > 15:

            result = {
                "status": "❌ Invalid Format",
                "risk": "MEDIUM",
                "message": (
                    "The phone number is longer than "
                    "a normal international number."
                )
            }

        else:

            result = {
                "status": "✅ Basic Format Valid",
                "risk": "LOW",
                "message": (
                    "The phone number has a basic "
                    "valid-looking format. This does not "
                    "verify the owner or prove that the "
                    "number is safe."
                )
            }

    return render(
        request,
        "shield/phone checker.html",
        {"result": result}
    )


# ============================================================
# SCREENSHOT SCANNER
# ============================================================

def screenshot_scanner(request):

    result = None

    if request.method == "POST":

        screenshot = request.FILES.get("screenshot")

        if not screenshot:

            result = {
                "risk": "UNKNOWN",
                "message": "Please select a screenshot."
            }

        else:

            allowed_types = [
                "image/jpeg",
                "image/png",
                "image/webp"
            ]

            max_size = 5 * 1024 * 1024

            if screenshot.content_type not in allowed_types:

                result = {
                    "risk": "MEDIUM",
                    "message": (
                        "Unsupported image format. "
                        "Please upload JPG, PNG or WEBP."
                    )
                }

            elif screenshot.size > max_size:

                result = {
                    "risk": "MEDIUM",
                    "message": (
                        "The screenshot is too large. "
                        "Maximum size is 5 MB."
                    )
                }

            else:

                result = {
                    "risk": "LOW",
                    "message": (
                        "Screenshot uploaded successfully. "
                        "Basic file validation passed."
                    )
                }

    return render(
        request,
        "shield/screenshot scanner.html",
        {"result": result}
    )