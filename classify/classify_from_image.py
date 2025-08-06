import pytesseract
import cv2
import os
import joblib

# 🔧 CONFIGURATION
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA_PATH = r"C:\Program Files\Tesseract-OCR"

# 📄 Nom de l’image à analyser
IMAGE_PATH = "jugement_page1_rep-fr-2cb26.jpg"

# 🔌 Lier Tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH

# 📤 Charger le modèle de classification
try:
    model = joblib.load("doc_classifier.joblib")
except FileNotFoundError:
    print("❌ Modèle doc_classifier.joblib non trouvé. Lance d'abord train_classifier.py.")
    exit()

# 📂 Charger l’image
image = cv2.imread(IMAGE_PATH)
if image is None:
    print(f"❌ L’image {IMAGE_PATH} est introuvable.")
    exit()

# 🎛️ Prétraitement pour l’OCR
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 🔍 OCR
try:
    texte = pytesseract.image_to_string(gray, lang="fra")
    print("📝 Texte extrait :")
    print("-" * 30)
    print(texte[:500])  # on affiche max 500 caractères
except Exception as e:
    print("❌ Erreur OCR :", e)
    exit()

# 🤖 Prédiction du type de document
prediction = model.predict([texte])[0]
probabilities = model.predict_proba([texte])[0]
confidence = max(probabilities) * 100

print("\n🔍 Prédiction :")
print(f"➡️ Type de document : {prediction}")
print(f"🎯 Confiance : {confidence:.2f}%")
