import os
import pytesseract
import cv2
import joblib
from docx import Document
import csv

# ⚙️ Configuration
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
DOCS_FOLDER = "docs_simules"
OUTPUT_CSV = "resultats.csv"

# Initialisation
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = os.path.dirname(TESSERACT_PATH)

# Charger le modèle
model = joblib.load("doc_classifier.joblib")

def extract_text_from_docx(path):
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        print(f"❌ Erreur lecture DOCX : {path} -> {e}")
        return ""

# Parcours et prédiction
results = []
for filename in os.listdir(DOCS_FOLDER):
    if not filename.endswith(".docx"):
        continue

    file_path = os.path.join(DOCS_FOLDER, filename)
    print(f"🔍 Traitement : {filename}")
    texte = extract_text_from_docx(file_path)

    if not texte.strip():
        print("⚠️ Aucun texte détecté.")
        results.append((filename, "erreur", 0))
        continue

    try:
        prediction = model.predict([texte])[0]
        confidence = max(model.predict_proba([texte])[0]) * 100
        results.append((filename, prediction, round(confidence, 2)))
    except Exception as e:
        print(f"❌ Erreur de prédiction : {e}")
        results.append((filename, "erreur", 0))

# Écriture CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["fichier", "prediction", "confiance (%)"])
    writer.writerows(results)

print(f"\n✅ Résultats enregistrés dans : {OUTPUT_CSV}")
