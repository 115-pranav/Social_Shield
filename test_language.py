from shield.multilingual import detect_language


messages = [
    "Your bank account will be blocked. Click this link.",
    "आपका बैंक खाता बंद कर दिया जाएगा।",
    "మీ బ్యాంక్ ఖాతా త్వరలో బ్లాక్ చేయబడుతుంది.",
    "Votre compte bancaire sera bloqué.",
    "Ihr Bankkonto wird gesperrt.",
    "Su cuenta bancaria será bloqueada.",
    "あなたの銀行口座は停止されます。",
    "Ваш банковский счет будет заблокирован.",
    "حسابك المصرفي سيتم حظره.",
]


for message in messages:

    language_name, language_code = detect_language(message)

    print("----------------------------------------")
    print("Message:", message)
    print("Language:", language_name)
    print("Code:", language_code)