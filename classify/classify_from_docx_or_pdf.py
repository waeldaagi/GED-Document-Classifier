import os
import pytesseract
import cv2
import joblib
from docx import Document
from pdf2image import convert_from_path
import tempfile

# ⚙️ Configuration
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR"
POPPLER_PATH = r"C:\Users\wael daagi\Desktop\GED_Document_Classifier\poppler-24.08.0\Library\bin"  

# Charger modèle IA
model = joblib.load("doc_classifier.joblib")

# OCR depuis image
def ocr_from_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray, lang="fra")

# Texte depuis .docx
def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

# Texte depuis .pdf
def extract_text_from_pdf(path):
    pages = convert_from_path(path, dpi=300, poppler_path=POPPLER_PATH)
    text = ""
    for page in pages:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            page.save(f.name, "PNG")
            image = cv2.imread(f.name)
            text += ocr_from_image(image) + "\n"
            os.remove(f.name)
    return text

# 📄 Spécifie le fichier à tester ici :
file_path = "docs_simules/jugement.docx"  # ⚠️ change ce chemin si besoin

# Analyse du fichier
if file_path.endswith(".docx"):
    texte = extract_text_from_docx(file_path)
elif file_path.endswith(".pdf"):
    texte = extract_text_from_pdf(file_path)
else:
    raise ValueError("Format non supporté (PDF ou DOCX uniquement).")

# IA
prediction = model.predict([texte])[0]
score = max(model.predict_proba([texte])[0]) * 100

# Résultat
print("📝 Texte extrait (début) :")
print(texte[:300] + "...")
print("\n📊 Type de document prédit :", prediction)
print(f"🎯 Confiance : {score:.2f}%")
