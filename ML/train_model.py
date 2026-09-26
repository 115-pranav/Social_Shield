import pandas as pd
import joblib

from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# Get the project folder
BASE_DIR = Path(__file__).resolve().parent

# Dataset location
DATASET_PATH = BASE_DIR / "dataset" / "messages.csv"

# Model output location
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "social_shield_model.pkl"


# Create model folder if it doesn't exist
MODEL_DIR.mkdir(exist_ok=True)


# Load dataset
data = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully.")
print("Number of messages:", len(data))

print("\nCategories:")
print(data["label"].value_counts())


# Input and output
X = data["text"]
y = data["label"]


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# Create ML pipeline
model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=1000
        )
    )
])


# Train model
print("\nTraining Social Shield model...")

model.fit(X_train, y_train)


# Test model
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nModel training completed.")
print("Accuracy:", round(accuracy * 100, 2), "%")


print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))


# Save model
joblib.dump(model, MODEL_PATH)

print("\nModel saved successfully!")
print("Location:", MODEL_PATH)