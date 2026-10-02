from pathlib import Path
import csv
import re

import joblib
from openai import OpenAI
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

    return render(
        request,
        "shield/screenshot scanner.html",
        {"result": result}
    )
def chatbot(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=405
        )

    message = request.POST.get("message", "").strip()

    if not message:
        return JsonResponse(
            {"error": "Please enter a message."},
            status=400
        )

    text = message.lower()

    # -----------------------------------------
    # SOCIAL SHIELD SMART CYBERSECURITY RULES
    # -----------------------------------------

    # 1. Phishing / suspicious links
    if (
        ("bank" in text or "account" in text or "payment" in text)
        and (
            "link" in text
            or "click" in text
            or "verify" in text
            or "blocked" in text
            or "suspend" in text
        )
    ) or any(word in text for word in [
        "phishing",
        "phish",
        "fake website",
        "suspicious link"
    ]):
        answer = (
            "⚠️ This sounds like a possible phishing attempt. "
            "Messages claiming that your bank account will be blocked "
            "and asking you to click a link are common warning signs. "
            "Do not click the link or provide passwords, OTPs, PINs, "
            "or banking information. Instead, open your bank's official "
            "app or website directly and check your account there."
        )

    # 2. OTP requests
    elif any(word in text for word in [
        "otp",
        "one time password",
        "verification code"
    ]):
        answer = (
            "🔐 Never share an OTP or verification code with another person. "
            "If someone unexpectedly asks for one, treat the request as "
            "suspicious. Verify the activity directly through the official "
            "app or website."
        )

    # 3. Password / credentials
    elif any(word in text for word in [
        "password",
        "login details",
        "username",
        "credentials"
    ]):
        answer = (
            "🔑 Keep your passwords private and use strong, unique passwords "
            "for important accounts. Never provide passwords through "
            "unexpected messages or links. Enable multi-factor authentication "
            "when available."
        )

    # 4. Prize / lottery / reward scams
    elif any(word in text for word in [
        "lottery",
        "prize",
        "winner",
        "won money",
        "free money",
        "reward",
        "gift card"
    ]):
        answer = (
            "🎁 Be careful with unexpected prize or reward messages. "
            "Scammers may claim that you won something and then request "
            "money or personal information. Don't click unknown links or "
            "send payment to claim an unexpected prize."
        )

    # 5. Scam
    elif any(word in text for word in [
        "scam",
        "fraud",
        "cheated",
        "fake message",
        "fake offer"
    ]):
        answer = (
            "🚨 This may involve a scam. Avoid sending money or personal "
            "information until you verify who contacted you. Check the "
            "information using an official website, app, or contact method "
            "rather than using links or phone numbers provided in the "
            "suspicious message."
        )

    # 6. Suspicious messages / links
    elif any(word in text for word in [
        "suspicious",
        "strange message",
        "unknown sender",
        "unknown number",
        "suspicious message",
        "suspicious website",
        "unknown link"
    ]):
        answer = (
            "⚠️ A suspicious message should be treated carefully. "
            "Avoid clicking links or opening unexpected attachments. "
            "Check the sender independently and verify the request "
            "through an official source."
        )

    # 7. Spam
    elif any(word in text for word in [
        "spam",
        "unwanted message",
        "advertisement message",
        "junk message"
    ]):
        answer = (
            "📩 Spam refers to unwanted or unsolicited messages. "
            "Some spam is simply advertising, while other messages "
            "may contain scams or malicious links. Avoid interacting "
            "with suspicious spam and report or block it when appropriate."
        )

    # 8. General phishing
    elif any(word in text for word in [
        "phishing",
        "phish"
    ]):
        answer = (
            "🎣 Phishing is a cyber scam designed to trick people into "
            "revealing sensitive information or interacting with a "
            "malicious website or message. Common warning signs include "
            "urgent requests, unexpected links, fake login pages, and "
            "requests for passwords or OTPs."
        )

    # 9. Cybersecurity
    elif any(word in text for word in [
        "cybersecurity",
        "cyber security",
        "online safety",
        "internet safety"
    ]):
        answer = (
            "🛡️ Cybersecurity means protecting devices, accounts, "
            "networks, and personal information from digital threats. "
            "Useful habits include using strong passwords, enabling "
            "multi-factor authentication, updating software, and "
            "being careful with unexpected links and messages."
        )

    # 10. Safe browsing
    elif any(word in text for word in [
        "safe online",
        "stay safe",
        "protect myself",
        "online protection"
    ]):
        answer = (
            "🛡️ For safer online activity, use strong unique passwords, "
            "enable multi-factor authentication, keep your software updated, "
            "avoid unexpected links, and verify important requests through "
            "official sources."
        )

    # 11. Greetings
    elif any(word in text for word in [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good evening"
    ]):
        answer = (
            "👋 Hello! I'm the Social Shield AI Assistant. "
            "Ask me about phishing, spam, scams, suspicious messages, "
            "online safety, or cybersecurity."
        )

    # 12. Default response
    else:
        answer = (
            "🤖 I'm the Social Shield AI Assistant. I can help explain "
            "phishing, spam, scams, suspicious messages, OTP safety, "
            "password safety, online security, and cybersecurity threats. "
            "You can describe a suspicious message to me and I'll explain "
            "the warning signs."
        )

    return JsonResponse({
        "answer": answer
    })