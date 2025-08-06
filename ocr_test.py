import pytesseract
import cv2
import os

# ✅ Chemin correct vers Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR"

# 📂 Charger l’image test
image = cv2.imread("test_doc.jpg")
if image is None:
    print("❌ L'image test_doc.jpg est introuvable.")
    exit()

if image is None:
    print("❌ L'image test_doc.png est introuvable.")
    exit()

# 🧼 Conversion en niveaux de gris
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 🔍 Extraction OCR
try:
    texte = pytesseract.image_to_string(gray, lang="fra")
    print("✅ Texte extrait :\n")
    print(texte)
except Exception as e:
    print("❌ Erreur lors de l'extraction OCR :", e)
