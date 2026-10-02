import pandas as pd
import joblib

from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "dataset" / "messages_multilingual.csv"

MODEL_DIR = BASE_DIR / "model"

# New model name - keeps the old model safe
MODEL_PATH = MODEL_DIR / "social_shield_multilingual_model.pkl"


# Create model directory
MODEL_DIR.mkdir(exist_ok=True)


# ==========================================
# LOAD DATASET
# ==========================================

print("Loading multilingual dataset...")

data = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully.")
print("Total messages:", len(data))


# ==========================================
# SHOW CATEGORY COUNTS
# ==========================================

print("\nCategory distribution:")

print(data["label"].value_counts())


# ==========================================
# INPUT AND OUTPUT
# ==========================================

X = data["text"].astype(str)

y = data["label"].astype(str)


# ==========================================
# SPLIT DATASET
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining examples:", len(X_train))
print("Testing examples:", len(X_test))


# ==========================================
# CREATE ML PIPELINE
# ==========================================

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            analyzer="char_wb",
            min_df=1
        )
    ),

    (
        "classifier",
        LogisticRegression(
            max_iter=2000,
            class_weight="balanced"
        )
    )
])


# ==========================================
# TRAIN MODEL
# ==========================================

print("\nTraining multilingual Social Shield model...")

model.fit(X_train, y_train)


# ==========================================
# TEST MODEL
# ==========================================

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)


print("\n==========================================")
print("MODEL TRAINING COMPLETED")
print("==========================================")

print(
    "Test Accuracy:",
    round(accuracy * 100, 2),
    "%"
)


# ==========================================
# CLASSIFICATION REPORT
# ==========================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(model, MODEL_PATH)


print("\n==========================================")
print("MODEL SAVED SUCCESSFULLY")
print("==========================================")

print("Location:", MODEL_PATH)