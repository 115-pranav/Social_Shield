from pathlib import Path
import csv
import re
import ipaddress
from urllib.parse import urlparse

import cv2
import numpy as np
import joblib

from openai import OpenAI
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .models import Analysis


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "ML"
    / "model"
    / "social_shield_multilingual_model.pkl"
)

model = joblib.load(MODEL_PATH)


# =========================================================
# HOME
# =========================================================

def home(request):
    return render(request, "shield/home.html")


# =========================================================
# MESSAGE ANALYZER
# =========================================================

def analyze_message(request):

    if request.method == "GET":
        return render(request, "shield/analyze.html")

    if request.method != "POST":
        return JsonResponse(
            {
                "error": "Only GET and POST requests are allowed."
            },
            status=405
        )

    message = request.POST.get("message", "").strip()

    if not message:
        return JsonResponse(
            {
                "error": "Please enter a message."
            },
            status=400
        )

    # -----------------------------------------
    # MULTILINGUAL LANGUAGE DETECTION
    # -----------------------------------------

    from .multilingual import detect_language

    language_name, language_code = detect_language(message)

    # -----------------------------------------
    # ML ANALYSIS
    # -----------------------------------------

    prediction = model.predict([message])[0]

    probabilities = model.predict_proba([message])[0]

    confidence = round(
        max(probabilities) * 100,
        2
    )

    # -----------------------------------------
    # RISK LEVEL
    # -----------------------------------------

    risk_levels = {
        "Safe": "LOW",
        "Spam": "HIGH",
        "Phishing": "CRITICAL",
        "Suspicious": "MEDIUM",
        "Abusive": "HIGH",
    }

    risk = risk_levels.get(
        prediction,
        "UNKNOWN"
    )

    # -----------------------------------------
    # URL DETECTION
    # -----------------------------------------

    has_url = bool(
        re.search(
            r"https?://\S+|www\.\S+",
            message,
            re.IGNORECASE
        )
    )

    # -----------------------------------------
    # SAVE ANALYSIS
    # -----------------------------------------

    Analysis.objects.create(
        user=(
            request.user
            if request.user.is_authenticated
            else None
        ),
        message=message,
        category=prediction,
        risk_level=risk,
        confidence=confidence,
    )

    # -----------------------------------------
    # RETURN RESULT
    # -----------------------------------------

    return JsonResponse(
        {
            "category": prediction,
            "risk": risk,
            "confidence": confidence,
            "has_url": has_url,
            "language": language_name,
            "language_code": language_code,
        }
    )


# =========================================================
# HISTORY
# =========================================================

def history(request):

    if not request.user.is_authenticated:
        return redirect("login")

    analyses = (
        Analysis.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "shield/history.html",
        {
            "analyses": analyses
        }
    )


# =========================================================
# DASHBOARD
# =========================================================

def dashboard(request):

    if not request.user.is_authenticated:
        return redirect("login")

    user_analyses = Analysis.objects.filter(
        user=request.user
    )

    context = {
        "total": user_analyses.count(),

        "safe": user_analyses.filter(
            category="Safe"
        ).count(),

        "spam": user_analyses.filter(
            category="Spam"
        ).count(),

        "phishing": user_analyses.filter(
            category="Phishing"
        ).count(),

        "suspicious": user_analyses.filter(
            category="Suspicious"
        ).count(),

        "abusive": user_analyses.filter(
            category="Abusive"
        ).count(),

        "recent": user_analyses.order_by(
            "-created_at"
        )[:10],
    }

    return render(
        request,
        "shield/dashboard.html",
        context
    )


# =========================================================
# REGISTER
# =========================================================

def register_user(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not username or not email or not password:

            return render(
                request,
                "shield/register.html",
                {
                    "error": "Please fill in all fields."
                }
            )

        if password != confirm_password:

            return render(
                request,
                "shield/register.html",
                {
                    "error": "Passwords do not match."
                }
            )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "shield/register.html",
                {
                    "error": "Username already exists."
                }
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        return redirect("login")

    return render(
        request,
        "shield/register.html"
    )


# =========================================================
# LOGIN
# =========================================================

def login_user(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect("home")

        return render(
            request,
            "shield/login.html",
            {
                "error": "Invalid username or password."
            }
        )

    return render(
        request,
        "shield/login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_user(request):

    logout(request)

    return redirect("home")


# =========================================================
# DOWNLOAD USER DATA
# =========================================================

def download_data(request):

    if not request.user.is_authenticated:
        return redirect("login")

    analyses = (
        Analysis.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="social_shield_my_data.csv"'
    )

    writer = csv.writer(response)

    writer.writerow(
        [
            "Date",
            "Message",
            "Category",
            "Risk Level",
            "Confidence"
        ]
    )

    for analysis in analyses:

        writer.writerow(
            [
                analysis.created_at.strftime(
                    "%d-%m-%Y %H:%M"
                ),
                analysis.message,
                analysis.category,
                analysis.risk_level,
                analysis.confidence,
            ]
        )

    return response


# =========================================================
# DELETE USER DATA
# =========================================================

def delete_my_data(request):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":

        Analysis.objects.filter(
            user=request.user
        ).delete()

    return redirect("dashboard")


# =========================================================
# SOCIAL SHIELD AI CHATBOT
# =========================================================

def chatbot(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Only POST requests are allowed."
            },
            status=405
        )

    message = request.POST.get(
        "message",
        ""
    ).strip()

    if not message:

        return JsonResponse(
            {
                "error": "Please enter a message."
            },
            status=400
        )

    text = message.lower()

    # -----------------------------------------
    # 1. PHISHING / SUSPICIOUS LINKS
    # -----------------------------------------

    if (
        (
            "bank" in text
            or "account" in text
            or "payment" in text
        )
        and
        (
            "link" in text
            or "click" in text
            or "verify" in text
            or "blocked" in text
            or "suspend" in text
        )
    ) or any(
        word in text
        for word in [
            "phishing",
            "phish",
            "fake website",
            "suspicious link"
        ]
    ):

        answer = (
            "⚠️ This sounds like a possible phishing attempt. "
            "Messages claiming that your bank account will be "
            "blocked and asking you to click a link are common "
            "warning signs. Do not click the link or provide "
            "passwords, OTPs, PINs, or banking information. "
            "Instead, open your bank's official app or website "
            "directly and check your account there."
        )

    # -----------------------------------------
    # 2. OTP
    # -----------------------------------------

    elif any(
        word in text
        for word in [
            "otp",
            "one time password",
            "verification code"
        ]
    ):

        answer = (
            "🔐 Never share an OTP or verification code "
            "with another person. If someone unexpectedly "
            "asks for one, treat the request as suspicious. "
            "Verify the activity directly through the "
            "official app or website."
        )

    # -----------------------------------------
    # 3. PASSWORD / CREDENTIALS
    # -----------------------------------------

    elif any(
        word in text
        for word in [
            "password",
            "login details",
            "username",
            "credentials"
        ]
    ):

        answer = (
            "🔑 Keep your passwords private and use strong, "
            "unique passwords for important accounts. Never "
            "provide passwords through unexpected messages "
            "or links. Enable multi-factor authentication "
            "when available."
        )

    # -----------------------------------------
    # 4. PRIZE / LOTTERY
    # -----------------------------------------

    elif any(
        word in text
        for word in [
            "lottery",
            "prize",
            "winner",
            "won money",
            "free money",
            "reward",
            "gift card"
        ]
    ):

        answer = (
            "🎁 Be careful with unexpected prize or reward "
            "messages. Scammers may claim that you won "
            "something and then request money or personal "
            "information. Don't click unknown links or "
            "send payment to claim an unexpected prize."
        )

    # -----------------------------------------
    # 5. SCAM
    # -----------------------------------------

    elif any(
        word in text
        for word in [
            "scam",
            "fraud",
            "cheated",
            "fake message",
            "fake offer"
        ]
    ):

        answer = (
            "🚨 This may involve a scam. Avoid sending money "
            "or personal information until you verify who "
            "contacted you. Check the information using an "
            "official website, app, or contact method rather "
            "than using links or phone numbers provided in "
            "the suspicious message."
        )

    # -----------------------------------------
    # 6. SUSPICIOUS MESSAGE
    # -----------------------------------------

    elif any(
        word in text
        for word in [
            "suspicious",
            "strange message",
            "unknown sender",
            "unknown number",
            "suspicious message",
            "suspicious website",
            "unknown link"
        ]
    ):

        answer = (
            "⚠️ A suspicious message should be treated "
            "carefully. Avoid clicking links or opening "
            "unexpected attachments. Check the sender "
            "independently and verify the request through "
            "an official source."
        )

    # -----------------------------------------
    # 7. SPAM
    # -----------------------------------------

    elif any(
        word in text
        for word in [
            "spam",
            "unwanted message",
            "advertisement message",
            "junk message"
        ]
    ):

        answer = (
            "📩 Spam refers to unwanted or unsolicited "
            "messages. Some spam is simply advertising, "
            "while other messages may contain scams or "
            "malicious links. Avoid interacting with "
            "suspicious spam and report or block it when "
            "appropriate."
        )

    # -----------------------------------------
    # 8. GENERAL PHISHING
    # -----------------------------------------

    elif any(
        word in text
        for word in [
            "phishing",
            "phish"
        ]
    ):

        answer = (
            "🎣 Phishing is a cyber scam designed to trick "
            "people into revealing sensitive information "
            "or interacting with a malicious website or "
            "message. Common warning signs include urgent "
            "requests, unexpected links, fake login pages, "
            "and requests for passwords or OTPs."
        )

    # -----------------------------------------
    # 9. CYBERSECURITY
    # -----------------------------------------

    elif any(
        word in text
        for word in [
            "cybersecurity",
            "cyber security",
            "online safety",
            "internet safety"
        ]
    ):

        answer = (
            "🛡️ Cybersecurity means protecting devices, "
            "accounts, networks, and personal information "
            "from digital threats. Useful habits include "
            "using strong passwords, enabling multi-factor "
            "authentication, updating software, and being "
            "careful with unexpected links and messages."
        )

    # -----------------------------------------
    # 10. SAFE BROWSING
    # -----------------------------------------

    elif any(
        word in text
        for word in [
            "safe online",
            "stay safe",
            "protect myself",
            "online protection"
        ]
    ):

        answer = (
            "🛡️ For safer online activity, use strong unique "
            "passwords, enable multi-factor authentication, "
            "keep your software updated, avoid unexpected "
            "links, and verify important requests through "
            "official sources."
        )

    # -----------------------------------------
    # 11. GREETINGS
    # -----------------------------------------

    elif any(
        word in text
        for word in [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good evening"
        ]
    ):

        answer = (
            "👋 Hello! I'm the Social Shield AI Assistant. "
            "Ask me about phishing, spam, scams, suspicious "
            "messages, online safety, or cybersecurity."
        )

    # -----------------------------------------
    # 12. DEFAULT
    # -----------------------------------------

    else:

        answer = (
            "🤖 I'm the Social Shield AI Assistant. "
            "I can help explain phishing, spam, scams, "
            "suspicious messages, OTP safety, password "
            "safety, online security, and cybersecurity "
            "threats. You can describe a suspicious "
            "message to me and I'll explain the warning signs."
        )

    return JsonResponse(
        {
            "answer": answer
        }
    )


# =========================================================
# QR URL SECURITY ANALYZER
# =========================================================

def analyze_qr_url(url):
    """
    Performs basic security checks on a QR-decoded URL.

    This is a heuristic security check.
    It does not prove that a website is malicious or safe.
    """

    original_url = url.strip()
    normalized_url = original_url

    # -----------------------------------------
    # NORMALIZE WWW URL
    # -----------------------------------------

    if normalized_url.lower().startswith("www."):
        normalized_url = "https://" + normalized_url

    # -----------------------------------------
    # PARSE URL
    # -----------------------------------------

    try:

        parsed = urlparse(
            normalized_url
        )

        hostname = parsed.hostname or ""
        hostname = hostname.lower()

    except Exception:

        return (
            "MEDIUM",
            [
                "The QR code contains a URL that could not be parsed normally."
            ]
        )

    indicators = []

    # -----------------------------------------
    # 1. INVALID / MISSING HOSTNAME
    # -----------------------------------------

    if not hostname:

        indicators.append(
            "The URL does not contain a recognizable domain name."
        )

    # -----------------------------------------
    # 2. IP ADDRESS
    # -----------------------------------------

    if hostname:

        try:

            ipaddress.ip_address(
                hostname
            )

            indicators.append(
                "The website uses an IP address instead of a normal domain name."
            )

        except ValueError:
            pass

    # -----------------------------------------
    # 3. HTTP WITHOUT HTTPS
    # -----------------------------------------

    if parsed.scheme.lower() == "http":

        indicators.append(
            "The URL uses HTTP instead of HTTPS."
        )

    # -----------------------------------------
    # 4. @ SYMBOL
    # -----------------------------------------

    if "@" in parsed.netloc:

        indicators.append(
            "The URL contains an @ symbol, which can make the actual destination harder to recognize."
        )

    # -----------------------------------------
    # 5. PUNYCODE
    # -----------------------------------------

    if "xn--" in hostname:

        indicators.append(
            "The domain contains punycode, which can sometimes be used to create look-alike domains."
        )

    # -----------------------------------------
    # 6. VERY LONG DOMAIN
    # -----------------------------------------

    if len(hostname) > 60:

        indicators.append(
            "The domain name is unusually long."
        )

    # -----------------------------------------
    # 7. MANY SUBDOMAINS
    # -----------------------------------------

    if hostname.count(".") >= 4:

        indicators.append(
            "The domain contains an unusually large number of subdomains."
        )

    # -----------------------------------------
    # 8. SUSPICIOUS KEYWORDS
    # -----------------------------------------

    suspicious_keywords = [
        "login",
        "verify",
        "verification",
        "account",
        "secure",
        "security",
        "update",
        "password",
        "credential",
        "otp",
        "payment",
        "wallet",
        "bank",
        "signin",
        "confirm",
        "unlock",
        "suspended",
        "claim",
        "prize",
        "reward",
        "gift",
        "free",
    ]

    url_text = (
        hostname
        + " "
        + parsed.path.lower()
        + " "
        + parsed.query.lower()
    )

    found_keywords = []

    for keyword in suspicious_keywords:

        if keyword in url_text:

            found_keywords.append(
                keyword
            )

    if found_keywords:

        unique_keywords = list(
            dict.fromkeys(found_keywords)
        )

        indicators.append(
            "The URL contains security-sensitive or promotional keywords: "
            + ", ".join(unique_keywords[:5])
            + "."
        )

    # -----------------------------------------
    # 9. VERY LONG URL
    # -----------------------------------------

    if len(original_url) > 180:

        indicators.append(
            "The complete URL is unusually long."
        )

    # -----------------------------------------
    # 10. MANY SPECIAL CHARACTERS
    # -----------------------------------------

    special_character_count = len(
        re.findall(
            r"[%_=+]",
            original_url
        )
    )

    if special_character_count >= 8:

        indicators.append(
            "The URL contains an unusually high number of special characters."
        )

    # -----------------------------------------
    # 11. EXCESSIVE PATH DEPTH
    # -----------------------------------------

    path_parts = [
        part
        for part in parsed.path.split("/")
        if part
    ]

    if len(path_parts) >= 6:

        indicators.append(
            "The URL contains an unusually deep path structure."
        )

    # -----------------------------------------
    # CALCULATE RISK
    # -----------------------------------------

    score = 0

    for indicator in indicators:

        if (
            "IP address" in indicator
            or "@ symbol" in indicator
            or "punycode" in indicator
        ):

            score += 3

        elif (
            "HTTP instead of HTTPS" in indicator
            or "security-sensitive" in indicator
            or "promotional keywords" in indicator
        ):

            score += 2

        else:

            score += 1

    # -----------------------------------------
    # RISK LEVEL
    # -----------------------------------------

    if not hostname:

        risk = "MEDIUM"

    elif score >= 6:

        risk = "HIGH"

    elif score >= 3:

        risk = "MEDIUM"

    else:

        risk = "LOW"

    # -----------------------------------------
    # NO WARNING INDICATORS
    # -----------------------------------------

    if not indicators:

        indicators.append(
            "No obvious URL warning signs were detected by the basic security checks."
        )

    return risk, indicators


# =========================================================
# QR CODE SCANNER
# =========================================================

def qr_scanner(request):

    # -----------------------------------------
    # OPEN QR SCANNER PAGE
    # -----------------------------------------

    if request.method == "GET":

        return render(
            request,
            "shield/qr_scanner.html"
        )

    # -----------------------------------------
    # ONLY POST ALLOWED FOR SCANNING
    # -----------------------------------------

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Only GET and POST requests are allowed."
            },
            status=405
        )

    # -----------------------------------------
    # GET UPLOADED IMAGE
    # -----------------------------------------

    qr_image = request.FILES.get(
        "qr_image"
    )

    if not qr_image:

        return JsonResponse(
            {
                "error": "Please upload a QR code image."
            },
            status=400
        )

    try:

        # -------------------------------------
        # READ IMAGE
        # -------------------------------------

        image_bytes = qr_image.read()

        if not image_bytes:

            return JsonResponse(
                {
                    "error": "The uploaded image is empty."
                },
                status=400
            )

        # -------------------------------------
        # CONVERT IMAGE TO NUMPY ARRAY
        # -------------------------------------

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        # -------------------------------------
        # DECODE IMAGE
        # -------------------------------------

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if image is None:

            return JsonResponse(
                {
                    "error": (
                        "The uploaded file could not "
                        "be read as an image."
                    )
                },
                status=400
            )

        # -------------------------------------
        # CREATE QR DETECTOR
        # -------------------------------------

        detector = cv2.QRCodeDetector()

        # -------------------------------------
        # FIRST QR DETECTION ATTEMPT
        # -------------------------------------

        decoded_text, points, _ = (
            detector.detectAndDecode(image)
        )

        # -------------------------------------
        # SECOND ATTEMPT
        # ENLARGE SMALL IMAGES
        # -------------------------------------

        if not decoded_text:

            height, width = image.shape[:2]

            if width < 1000 or height < 1000:

                enlarged = cv2.resize(
                    image,
                    None,
                    fx=2,
                    fy=2,
                    interpolation=cv2.INTER_CUBIC
                )

                decoded_text, points, _ = (
                    detector.detectAndDecode(
                        enlarged
                    )
                )

        # -------------------------------------
        # THIRD ATTEMPT
        # TRY GRAYSCALE
        # -------------------------------------

        if not decoded_text:

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            decoded_text, points, _ = (
                detector.detectAndDecode(
                    gray
                )
            )

        # -------------------------------------
        # QR NOT DETECTED
        # -------------------------------------

        if not decoded_text:

            print(
                "QR scanner could not decode the image."
            )

            return JsonResponse(
                {
                    "error": (
                        "The QR image was received correctly, "
                        "but the QR code could not be decoded. "
                        "Please make sure the complete QR code "
                        "is visible and has good contrast."
                    )
                },
                status=400
            )

        # -------------------------------------
        # CLEAN RESULT
        # -------------------------------------

        decoded_text = decoded_text.strip()

        # -------------------------------------
        # CHECK FOR URL
        # -------------------------------------

        is_url = bool(
            re.match(
                r"^(https?://|www\.)",
                decoded_text,
                re.IGNORECASE
            )
        )

        # -------------------------------------
        # URL SECURITY ANALYSIS
        # -------------------------------------

        if is_url:

            risk, indicators = analyze_qr_url(
                decoded_text
            )

            explanation = (
                "QR URL security analysis completed. "
                "The website was not opened automatically. "
                "The result is based on basic URL warning signs."
            )

        # -------------------------------------
        # NON-URL RESULT
        # -------------------------------------

        else:

            risk = "LOW"

            indicators = [
                "No website URL was detected in the QR content."
            ]

            explanation = (
                "The QR code contains text or other information "
                "rather than a detected website URL. Review "
                "the decoded content before using it."
            )

        # -------------------------------------
        # RETURN SUCCESS
        # -------------------------------------

        return JsonResponse(
            {
                "success": True,
                "decoded_text": decoded_text,
                "is_url": is_url,
                "risk": risk,
                "explanation": explanation,
                "indicators": indicators,
            }
        )

    # -----------------------------------------
    # ERROR HANDLING
    # -----------------------------------------

    except Exception as e:

        print(
            "QR SCANNER ERROR:",
            str(e)
        )

        return JsonResponse(
            {
                "error": (
                    "Unable to process the QR image. "
                    "Please try another clear QR image."
                )
            },
            status=400
        )