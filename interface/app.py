import streamlit as st
import pytesseract
import cv2
import joblib
import os
from pdf2image import convert_from_bytes
from docx import Document
from tempfile import NamedTemporaryFile
import numpy as np
from PIL import Image, Image as PILImage

# ⚙️ CONFIG
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"c:\Users\wael daagi\Desktop\GED_Document_Classifier\poppler-24.08.0\Library\bin"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = os.path.dirname(TESSERACT_PATH)

# 📥 Load model
model = joblib.load("data/model/doc_classifier.joblib")

# 🌟 Interface
st.set_page_config(page_title="GED Classifier", layout="centered")

# 🖼 Logo
logo = PILImage.open("data/logo/bfpme_logo.png")
st.image(logo, width=150)

st.title("\U0001F4C4 GED Document Classifier (PDF / DOCX / Image)")

# 📚 Fonctions OCR
def ocr_image(image_pil):
    image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray, lang="fra")

def ocr_pdf(file_bytes):
    text = ""
    pages = convert_from_bytes(file_bytes.read(), dpi=300, poppler_path=POPPLER_PATH)
    for page in pages:
        text += ocr_image(page) + "\n"
    return text

def ocr_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

# \U0001F5BC Interface Streamlit
uploaded_file = st.file_uploader("\U0001F4E4 Déposez un fichier .pdf, .docx, .jpg, .png :", type=["pdf", "docx", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    ext = uploaded_file.name.lower().split(".")[-1]

    with st.spinner("\U0001F50D Lecture du fichier et extraction OCR..."):
        if ext in ["jpg", "jpeg", "png"]:
            image = Image.open(uploaded_file)
            texte = ocr_image(image)
        elif ext == "pdf":
            texte = ocr_pdf(uploaded_file)
        elif ext == "docx":
            texte = ocr_docx(uploaded_file)
        else:
            st.error("❌ Format non pris en charge.")
            st.stop()

    st.subheader("\U0001F4DD Texte extrait :")
    st.text(texte[:1000] + "..." if len(texte) > 1000 else texte)

    if texte.strip():
        pred = model.predict([texte])[0]
        proba = max(model.predict_proba([texte])[0]) * 100
        st.success(f"\U0001F4CA Document classé comme : **{pred}**")
        st.info(f"\U0001F3AF Confiance : {proba:.2f} %")
    else:
        st.error("Aucun texte lisible détecté.")
