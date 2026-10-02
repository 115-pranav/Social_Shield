import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "dataset" / "messages_multilingual.csv"


data = [

    # =========================
    # SAFE
    # =========================

    ("Hello, how are you today?", "Safe"),
    ("Good morning, have a nice day.", "Safe"),
    ("Can you send me the project details?", "Safe"),
    ("Let's meet tomorrow for the project.", "Safe"),
    ("Thank you for your message.", "Safe"),
    ("Can you share the class notes with me?", "Safe"),
    ("The meeting starts at ten tomorrow.", "Safe"),
    ("Please send me the assignment file.", "Safe"),
    ("I will call you after class.", "Safe"),
    ("Thanks for helping me with the project.", "Safe"),

    ("హలో, మీరు ఈరోజు ఎలా ఉన్నారు?", "Safe"),
    ("శుభోదయం, మీ రోజు మంచిగా ఉండాలి.", "Safe"),
    ("ప్రాజెక్ట్ వివరాలను నాకు పంపగలరా?", "Safe"),
    ("రేపు ప్రాజెక్ట్ కోసం కలుద్దాం.", "Safe"),
    ("మీ సందేశానికి ధన్యవాదాలు.", "Safe"),
    ("క్లాస్ నోట్స్ నాకు పంపగలరా?", "Safe"),
    ("రేపు సమావేశం పది గంటలకు ప్రారంభమవుతుంది.", "Safe"),
    ("అసైన్‌మెంట్ ఫైల్ నాకు పంపండి.", "Safe"),
    ("క్లాస్ తర్వాత మీకు కాల్ చేస్తాను.", "Safe"),
    ("ప్రాజెక్ట్‌లో సహాయం చేసినందుకు ధన్యవాదాలు.", "Safe"),

    ("नमस्ते, आप आज कैसे हैं?", "Safe"),
    ("सुप्रभात, आपका दिन अच्छा रहे।", "Safe"),
    ("क्या आप मुझे प्रोजेक्ट की जानकारी भेज सकते हैं?", "Safe"),
    ("कल प्रोजेक्ट के लिए मिलते हैं।", "Safe"),
    ("आपके संदेश के लिए धन्यवाद।", "Safe"),
    ("क्या आप मुझे क्लास के नोट्स भेज सकते हैं?", "Safe"),
    ("मीटिंग कल दस बजे शुरू होगी।", "Safe"),
    ("कृपया असाइनमेंट फाइल मुझे भेजें।", "Safe"),
    ("मैं क्लास के बाद आपको फोन करूंगा।", "Safe"),
    ("प्रोजेक्ट में मदद करने के लिए धन्यवाद।", "Safe"),

    ("Bonjour, comment allez-vous aujourd'hui ?", "Safe"),
    ("Guten Morgen, ich wünsche Ihnen einen schönen Tag.", "Safe"),
    ("Hola, ¿cómo estás hoy?", "Safe"),
    ("Grazie per il tuo messaggio.", "Safe"),
    ("Je vous enverrai les détails du projet.", "Safe"),
    ("La réunion commence demain matin.", "Safe"),
    ("あなたは今日元気ですか？", "Safe"),
    ("今日はプロジェクトについて話しましょう。", "Safe"),
    ("오늘 좋은 하루 보내세요.", "Safe"),
    ("프로젝트 세부 정보를 보내주세요.", "Safe"),

    # =========================
    # SPAM
    # =========================

    ("Congratulations! You have won a free prize.", "Spam"),
    ("Win a free mobile phone now.", "Spam"),
    ("Limited offer claim your free reward today.", "Spam"),
    ("You have won a lottery prize.", "Spam"),
    ("Get free cash immediately.", "Spam"),
    ("Exclusive discount available today.", "Spam"),
    ("Claim your free gift before the offer ends.", "Spam"),
    ("You are selected for a special reward.", "Spam"),
    ("Free shopping voucher available now.", "Spam"),
    ("Congratulations, you are a lucky winner.", "Spam"),

    ("అభినందనలు! మీరు ఉచిత బహుమతి గెలుచుకున్నారు.", "Spam"),
    ("ఇప్పుడే ఉచిత మొబైల్ ఫోన్ గెలుచుకోండి.", "Spam"),
    ("పరిమిత ఆఫర్, మీ ఉచిత రివార్డ్‌ను పొందండి.", "Spam"),
    ("మీరు లాటరీ బహుమతి గెలుచుకున్నారు.", "Spam"),
    ("వెంటనే ఉచిత నగదు పొందండి.", "Spam"),
    ("ఈరోజు ప్రత్యేక డిస్కౌంట్ అందుబాటులో ఉంది.", "Spam"),
    ("ఆఫర్ ముగిసేలోపు మీ ఉచిత బహుమతిని పొందండి.", "Spam"),
    ("ప్రత్యేక రివార్డ్ కోసం మీరు ఎంపికయ్యారు.", "Spam"),
    ("ఉచిత షాపింగ్ వోచర్ ఇప్పుడు అందుబాటులో ఉంది.", "Spam"),
    ("అభినందనలు, మీరు అదృష్ట విజేత.", "Spam"),

    ("बधाई हो! आपने मुफ्त इनाम जीता है।", "Spam"),
    ("अभी मुफ्त मोबाइल फोन जीतें।", "Spam"),
    ("सीमित ऑफर, अपना मुफ्त रिवॉर्ड प्राप्त करें।", "Spam"),
    ("आपने लॉटरी का इनाम जीता है।", "Spam"),
    ("तुरंत मुफ्त नकद प्राप्त करें।", "Spam"),
    ("आज विशेष छूट उपलब्ध है।", "Spam"),
    ("ऑफर खत्म होने से पहले अपना मुफ्त उपहार लें।", "Spam"),
    ("आपको विशेष इनाम के लिए चुना गया है।", "Spam"),
    ("मुफ्त शॉपिंग वाउचर अभी उपलब्ध है।", "Spam"),
    ("बधाई हो, आप भाग्यशाली विजेता हैं।", "Spam"),

    ("Félicitations, vous avez gagné un cadeau gratuit.", "Spam"),
    ("Gagnez un téléphone gratuitement maintenant.", "Spam"),
    ("Offre limitée, réclamez votre récompense.", "Spam"),
    ("Vous avez gagné à la loterie.", "Spam"),
    ("Obtenez de l'argent gratuitement immédiatement.", "Spam"),
    ("Herzlichen Glückwunsch, Sie haben einen Preis gewonnen.", "Spam"),
    ("Gewinnen Sie jetzt ein kostenloses Mobiltelefon.", "Spam"),
    ("Sie wurden für eine besondere Belohnung ausgewählt.", "Spam"),
    ("¡Felicidades! Has ganado un premio gratis.", "Spam"),
    ("Obtén tu recompensa gratuita ahora.", "Spam"),

    # =========================
    # PHISHING
    # =========================

    ("Your account will be blocked. Verify your password now.", "Phishing"),
    ("Click this link to verify your bank account.", "Phishing"),
    ("Send your OTP to confirm your account.", "Phishing"),
    ("Your bank account needs verification. Click here.", "Phishing"),
    ("Enter your password to receive the reward.", "Phishing"),
    ("Your payment account needs urgent verification.", "Phishing"),
    ("Confirm your login details using this link.", "Phishing"),
    ("Your account has been suspended. Verify immediately.", "Phishing"),
    ("Provide your verification code to continue.", "Phishing"),
    ("Update your banking details through this link.", "Phishing"),

    ("మీ ఖాతా బ్లాక్ చేయబడుతుంది. వెంటనే మీ పాస్‌వర్డ్‌ను ధృవీకరించండి.", "Phishing"),
    ("మీ బ్యాంక్ ఖాతాను ధృవీకరించడానికి ఈ లింక్‌పై క్లిక్ చేయండి.", "Phishing"),
    ("మీ ఖాతాను నిర్ధారించడానికి మీ OTP పంపండి.", "Phishing"),
    ("మీ బ్యాంక్ ఖాతాకు ధృవీకరణ అవసరం. ఇక్కడ క్లిక్ చేయండి.", "Phishing"),
    ("రివార్డ్ పొందడానికి మీ పాస్‌వర్డ్‌ను నమోదు చేయండి.", "Phishing"),
    ("మీ చెల్లింపు ఖాతాకు అత్యవసర ధృవీకరణ అవసరం.", "Phishing"),
    ("ఈ లింక్ ఉపయోగించి మీ లాగిన్ వివరాలను నిర్ధారించండి.", "Phishing"),
    ("మీ ఖాతా నిలిపివేయబడింది. వెంటనే ధృవీకరించండి.", "Phishing"),
    ("కొనసాగించడానికి మీ వెరిఫికేషన్ కోడ్ ఇవ్వండి.", "Phishing"),
    ("ఈ లింక్ ద్వారా మీ బ్యాంకింగ్ వివరాలను నవీకరించండి.", "Phishing"),

    ("आपका खाता बंद कर दिया जाएगा। अभी अपना पासवर्ड सत्यापित करें।", "Phishing"),
    ("अपने बैंक खाते को सत्यापित करने के लिए इस लिंक पर क्लिक करें।", "Phishing"),
    ("अपना खाता सत्यापित करने के लिए OTP भेजें।", "Phishing"),
    ("आपके बैंक खाते का सत्यापन आवश्यक है। यहां क्लिक करें।", "Phishing"),
    ("इनाम पाने के लिए अपना पासवर्ड दर्ज करें।", "Phishing"),
    ("आपके भुगतान खाते के लिए तत्काल सत्यापन आवश्यक है।", "Phishing"),
    ("इस लिंक का उपयोग करके अपने लॉगिन विवरण की पुष्टि करें।", "Phishing"),
    ("आपका खाता निलंबित कर दिया गया है। तुरंत सत्यापित करें।", "Phishing"),
    ("जारी रखने के लिए अपना सत्यापन कोड दें।", "Phishing"),
    ("इस लिंक से अपनी बैंकिंग जानकारी अपडेट करें।", "Phishing"),

    ("Votre compte sera bloqué. Vérifiez votre mot de passe.", "Phishing"),
    ("Cliquez sur ce lien pour vérifier votre compte bancaire.", "Phishing"),
    ("Envoyez votre code OTP pour confirmer votre compte.", "Phishing"),
    ("Ihr Konto wird gesperrt. Bestätigen Sie jetzt Ihr Passwort.", "Phishing"),
    ("Klicken Sie auf diesen Link, um Ihr Bankkonto zu bestätigen.", "Phishing"),
    ("Ihr Bestätigungscode wird benötigt, um fortzufahren.", "Phishing"),
    ("Su cuenta será bloqueada. Verifique su contraseña.", "Phishing"),
    ("Haga clic en este enlace para verificar su cuenta bancaria.", "Phishing"),
    ("Envíe su código de verificación para continuar.", "Phishing"),
    ("Votre compte bancaire nécessite une vérification urgente.", "Phishing"),

    # =========================
    # SUSPICIOUS
    # =========================

    ("This message contains a suspicious link.", "Suspicious"),
    ("Please click this unknown link immediately.", "Suspicious"),
    ("Your account activity looks unusual.", "Suspicious"),
    ("Urgent action may be required on your account.", "Suspicious"),
    ("Verify your details using this link.", "Suspicious"),
    ("An unknown sender is asking for information.", "Suspicious"),
    ("This website address looks unusual.", "Suspicious"),
    ("You received a message from an unknown number.", "Suspicious"),
    ("The sender is asking you to act quickly.", "Suspicious"),
    ("This unexpected attachment should be checked carefully.", "Suspicious"),

    ("ఈ సందేశంలో అనుమానాస్పద లింక్ ఉంది.", "Suspicious"),
    ("తెలియని లింక్‌పై వెంటనే క్లిక్ చేయమని చెబుతోంది.", "Suspicious"),
    ("మీ ఖాతా కార్యకలాపం అసాధారణంగా కనిపిస్తోంది.", "Suspicious"),
    ("మీ ఖాతాపై అత్యవసర చర్య అవసరం కావచ్చు.", "Suspicious"),
    ("ఈ లింక్ ఉపయోగించి మీ వివరాలను ధృవీకరించండి.", "Suspicious"),
    ("తెలియని వ్యక్తి సమాచారం అడుగుతున్నారు.", "Suspicious"),
    ("ఈ వెబ్‌సైట్ చిరునామా అసాధారణంగా కనిపిస్తోంది.", "Suspicious"),
    ("తెలియని నంబర్ నుండి మీకు సందేశం వచ్చింది.", "Suspicious"),
    ("పంపిన వ్యక్తి మిమ్మల్ని త్వరగా చర్య తీసుకోమంటున్నారు.", "Suspicious"),
    ("ఈ అనుకోని అటాచ్‌మెంట్‌ను జాగ్రత్తగా తనిఖీ చేయండి.", "Suspicious"),

    ("इस संदेश में एक संदिग्ध लिंक है।", "Suspicious"),
    ("कृपया इस अज्ञात लिंक पर तुरंत क्लिक करें।", "Suspicious"),
    ("आपके खाते की गतिविधि असामान्य लग रही है।", "Suspicious"),
    ("आपके खाते पर तत्काल कार्रवाई की आवश्यकता हो सकती है।", "Suspicious"),
    ("इस लिंक का उपयोग करके अपने विवरण सत्यापित करें।", "Suspicious"),
    ("एक अज्ञात व्यक्ति जानकारी मांग रहा है।", "Suspicious"),
    ("इस वेबसाइट का पता असामान्य लग रहा है।", "Suspicious"),
    ("आपको किसी अज्ञात नंबर से संदेश मिला है।", "Suspicious"),
    ("प्रेषक आपको जल्दी कार्रवाई करने के लिए कह रहा है।", "Suspicious"),
    ("इस अनपेक्षित अटैचमेंट को सावधानी से जांचें।", "Suspicious"),

    ("Ce message contient un lien suspect.", "Suspicious"),
    ("Bitte überprüfen Sie diesen unbekannten Link sorgfältig.", "Suspicious"),
    ("La actividad de su cuenta parece inusual.", "Suspicious"),
    ("このメッセージには不審なリンクが含まれています。", "Suspicious"),
    ("이 메시지에는 의심스러운 링크가 있습니다.", "Suspicious"),
    ("Ваш аккаунт показывает необычную активность.", "Suspicious"),

    # =========================
    # ABUSIVE
    # =========================

    ("You are stupid and useless.", "Abusive"),
    ("Nobody likes you.", "Abusive"),
    ("Stop behaving like an idiot.", "Abusive"),
    ("You are a worthless person.", "Abusive"),
    ("Shut up you stupid fool.", "Abusive"),
    ("You are completely useless.", "Abusive"),
    ("You are acting like a fool.", "Abusive"),
    ("Stop insulting everyone.", "Abusive"),
    ("That was a very rude comment.", "Abusive"),
    ("Do not speak to people like that.", "Abusive"),

    ("నువ్వు చాలా పనికిరాని వ్యక్తివి.", "Abusive"),
    ("ఎవరూ నిన్ను ఇష్టపడరు.", "Abusive"),
    ("మూర్ఖుడిలా ప్రవర్తించడం ఆపు.", "Abusive"),
    ("నువ్వు విలువలేని వ్యక్తివి.", "Abusive"),
    ("నోరు మూసుకో, మూర్ఖుడా.", "Abusive"),
    ("నువ్వు పూర్తిగా పనికిరానివి.", "Abusive"),
    ("నువ్వు మూర్ఖుడిలా ప్రవర్తిస్తున్నావు.", "Abusive"),
    ("అందరినీ అవమానించడం ఆపు.", "Abusive"),
    ("అది చాలా అసభ్యకరమైన వ్యాఖ్య.", "Abusive"),
    ("ప్రజలతో అలా మాట్లాడవద్దు.", "Abusive"),

    ("तुम बहुत बेवकूफ और बेकार हो।", "Abusive"),
    ("कोई तुम्हें पसंद नहीं करता।", "Abusive"),
    ("मूर्ख की तरह व्यवहार करना बंद करो।", "Abusive"),
    ("तुम एक बेकार व्यक्ति हो।", "Abusive"),
    ("चुप रहो, बेवकूफ।", "Abusive"),
    ("तुम बिल्कुल बेकार हो।", "Abusive"),
    ("तुम मूर्ख की तरह व्यवहार कर रहे हो।", "Abusive"),
    ("सबका अपमान करना बंद करो।", "Abusive"),
    ("यह बहुत बदतमीजी वाली टिप्पणी है।", "Abusive"),
    ("लोगों से इस तरह बात मत करो।", "Abusive"),

    ("Tu es stupide et inutile.", "Abusive"),
    ("Du bist völlig nutzlos.", "Abusive"),
    ("Eres una persona inútil.", "Abusive"),
    ("あなたは役に立たない人です。", "Abusive"),
    ("너는 정말 쓸모없는 사람이야.", "Abusive"),
    ("Ты ведешь себя как глупец.", "Abusive"),
]


# Remove accidental duplicates while preserving order
unique_data = list(dict.fromkeys(data))


with open(OUTPUT_PATH, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["text", "label"])
    writer.writerows(unique_data)


print("Multilingual dataset created successfully.")
print("Location:", OUTPUT_PATH)
print("Total examples:", len(unique_data))

for label in ["Safe", "Spam", "Phishing", "Suspicious", "Abusive"]:
    count = sum(1 for _, current_label in unique_data if current_label == label)
    print(f"{label}: {count}")