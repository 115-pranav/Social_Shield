from lingua import Language, LanguageDetectorBuilder


# Use all languages available in the installed Lingua package
LANGUAGES = list(Language.all())

# Build the detector once when Django starts
detector = LanguageDetectorBuilder.from_languages(
    *LANGUAGES
).build()


def detect_language(text):
    """
    Detect the language of a message.

    Returns:
        language_name: Human-readable language name
        language_code: Simple language code
    """

    text = text.strip()

    if not text:
        return "Unknown", "unknown"

    detected = detector.detect_language_of(text)

    if detected is None:
        return "Unknown", "unknown"

    language_name = detected.name.replace("_", " ").title()

    language_codes = {
        "ENGLISH": "en",
        "HINDI": "hi",
        "TELUGU": "te",
        "TAMIL": "ta",
        "MALAYALAM": "ml",
        "BENGALI": "bn",
        "MARATHI": "mr",
        "GUJARATI": "gu",
        "PUNJABI": "pa",
        "URDU": "ur",
        "ARABIC": "ar",
        "FRENCH": "fr",
        "GERMAN": "de",
        "SPANISH": "es",
        "ITALIAN": "it",
        "PORTUGUESE": "pt",
        "RUSSIAN": "ru",
        "JAPANESE": "ja",
        "KOREAN": "ko",
        "CHINESE": "zh",
    }

    language_code = language_codes.get(
        detected.name,
        detected.name.lower()
    )

    return language_name, language_code