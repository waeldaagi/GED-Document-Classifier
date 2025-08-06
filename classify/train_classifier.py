import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# 📥 Charger le fichier CSV
df = pd.read_csv("c:/Users/wael daagi/Desktop/GED_Document_Classifier/data/dataset.csv")

# ✂️ Séparer les données
X = df["texte"]
y = df["label"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 🧠 Créer le modèle
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X_train, y_train)

# 📊 Évaluer le modèle
y_pred = model.predict(X_test)
print("🔍 Évaluation :\n")
print(classification_report(y_test, y_pred))

# 💾 Sauvegarde
joblib.dump(model, "doc_classifier.joblib")
print("✅ Nouveau modèle enregistré.")
