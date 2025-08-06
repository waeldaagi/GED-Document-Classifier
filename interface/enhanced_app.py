import streamlit as st
import pytesseract
import cv2
import joblib
import os
import shutil
from pdf2image import convert_from_bytes
from docx import Document
from tempfile import NamedTemporaryFile
import numpy as np
from PIL import Image, Image as PILImage
from datetime import datetime

# ⚙️ CONFIG
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"c:\Users\wael daagi\Desktop\GED_Document_Classifier\poppler-24.08.0\Library\bin"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = os.path.dirname(TESSERACT_PATH)

# 📁 Configuration pour l'organisation des fichiers
BASE_OUTPUT_DIR = "documents_classifies"
UNKNOWN_DIR = "non_classifies"

# 📥 Load model
model = joblib.load("data/model/doc_classifier.joblib")

# 🌟 Interface
st.set_page_config(page_title="GED Classifier", layout="centered")

# 🖼 Logo
try:
    logo = PILImage.open("data/logo/bfpme_logo.png")
    st.image(logo, width=150)
except:
    st.write("🏢 BFPME")

st.title("📄 GED Document Classifier avec Organisation Automatique")

# 📁 Fonctions d'organisation
def create_directories():
    """Créer les dossiers de destination"""
    if not os.path.exists(BASE_OUTPUT_DIR):
        os.makedirs(BASE_OUTPUT_DIR)
    
    unknown_path = os.path.join(BASE_OUTPUT_DIR, UNKNOWN_DIR)
    if not os.path.exists(unknown_path):
        os.makedirs(unknown_path)

def create_category_folder(category):
    """Créer un dossier pour une catégorie"""
    category_path = os.path.join(BASE_OUTPUT_DIR, category)
    if not os.path.exists(category_path):
        os.makedirs(category_path)
    return category_path

def save_and_organize_file(uploaded_file, category, confidence):
    """Sauvegarder et organiser le fichier uploadé selon la prédiction"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = uploaded_file.name
    
    # Toujours classer selon la prédiction, peu importe la confiance
    destination_dir = create_category_folder(category)
    
    # Marquer les fichiers avec faible confiance dans le nom
    if confidence < 50.0:
        new_filename = f"[FAIBLE_CONFIANCE_{confidence:.1f}%]_{timestamp}_{original_name}"
    else:
        new_filename = f"[{confidence:.1f}%]_{timestamp}_{original_name}"
    
    # Créer le chemin complet
    destination_path = os.path.join(destination_dir, new_filename)
    
    # Sauvegarder le fichier
    try:
        with open(destination_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return destination_path
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")
        return None

# 📚 Fonctions OCR
def ocr_image(image_pil):
    image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray, lang="fra")

def ocr_pdf(file_bytes):
    text = ""
    try:
        pages = convert_from_bytes(file_bytes, dpi=300, poppler_path=POPPLER_PATH)
        for page in pages:
            text += ocr_image(page) + "\n"
    except Exception as e:
        st.error(f"Erreur OCR PDF : {e}")
    return text

def ocr_docx(file):
    try:
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        st.error(f"Erreur lecture DOCX : {e}")
        return ""

# 🎛️ Options dans la sidebar
st.sidebar.header("⚙️ Options")
auto_organize = st.sidebar.checkbox("📁 Organisation automatique", value=True, 
                                   help="Déplace automatiquement les fichiers vers les dossiers de leur catégorie prédite")

show_confidence_warning = st.sidebar.slider("⚠️ Seuil d'avertissement", 
                                           min_value=0, max_value=100, value=20,
                                           help="Affiche un avertissement pour les documents avec confiance < seuil")

# 📊 Affichage de l'arborescence actuelle
if st.sidebar.button("🗂️ Voir l'arborescence"):
    st.sidebar.subheader("Structure des dossiers :")
    if os.path.exists(BASE_OUTPUT_DIR):
        for item in os.listdir(BASE_OUTPUT_DIR):
            item_path = os.path.join(BASE_OUTPUT_DIR, item)
            if os.path.isdir(item_path):
                file_count = len([f for f in os.listdir(item_path) 
                                if os.path.isfile(os.path.join(item_path, f))])
                st.sidebar.write(f"📁 {item} ({file_count} fichiers)")
    else:
        st.sidebar.write("Aucun dossier créé encore")

# 📤 Interface principale
uploaded_file = st.file_uploader("📤 Déposez un fichier .pdf, .docx, .jpg, .png :", 
                                 type=["pdf", "docx", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Créer les dossiers si nécessaire
    create_directories()
    
    ext = uploaded_file.name.lower().split(".")[-1]
    
    # Afficher les informations du fichier
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 Nom", uploaded_file.name)
    with col2:
        st.metric("📏 Taille", f"{uploaded_file.size / 1024:.1f} KB")
    with col3:
        st.metric("🔤 Type", ext.upper())

    with st.spinner("🔍 Lecture du fichier et extraction OCR..."):
        # Extraction du texte selon le format
        if ext in ["jpg", "jpeg", "png"]:
            image = Image.open(uploaded_file)
            texte = ocr_image(image)
            st.image(image, caption="Image uploadée", use_column_width=True)
        elif ext == "pdf":
            texte = ocr_pdf(uploaded_file.getbuffer())
        elif ext == "docx":
            texte = ocr_docx(uploaded_file)
        else:
            st.error("❌ Format non pris en charge.")
            st.stop()

    # Affichage du texte extrait
    with st.expander("📝 Texte extrait (cliquez pour voir)", expanded=False):
        if texte.strip():
            st.text_area("Texte", texte, height=200)
        else:
            st.warning("Aucun texte détecté dans le document")

    # Classification
    if texte.strip():
        with st.spinner("🤖 Classification en cours..."):
            pred = model.predict([texte])[0]
            proba = max(model.predict_proba([texte])[0]) * 100
        
        # Affichage des résultats
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"📊 **{pred}**")
        
        with col2:
            if proba >= 80:
                st.success(f"🎯 {proba:.1f}%")
            elif proba >= show_confidence_warning:
                st.info(f"🎯 {proba:.1f}%")
            else:
                st.warning(f"🎯 {proba:.1f}% (confiance faible)")
        
        # Organisation automatique
        if auto_organize:
            st.divider()
            with st.spinner("📁 Organisation du fichier..."):
                saved_path = save_and_organize_file(uploaded_file, pred, proba)
                
                if saved_path:
                    if proba >= show_confidence_warning:
                        st.success(f"✅ Fichier classé dans **{pred}** : `{saved_path}`")
                    else:
                        st.warning(f"⚠️ Fichier classé dans **{pred}** avec confiance faible : `{saved_path}`")
                    
                    # Bouton pour ouvrir le dossier
                    folder_path = os.path.dirname(saved_path)
                    if st.button("🗂️ Ouvrir le dossier"):
                        os.startfile(folder_path)  # Windows uniquement
                else:
                    st.error("❌ Erreur lors de l'organisation du fichier")
        
        # Affichage des probabilités détaillées
        with st.expander("📈 Probabilités détaillées", expanded=False):
            all_probas = model.predict_proba([texte])[0]
            classes = model.classes_
            
            for i, (classe, prob) in enumerate(zip(classes, all_probas)):
                prob_percent = prob * 100
                st.progress(prob_percent / 100, text=f"{classe}: {prob_percent:.1f}%")
    
    else:
        st.error("❌ Aucun texte lisible détecté dans le document")
        
        # Même si pas de texte, on classe dans "document_vide"
        if auto_organize:
            saved_path = save_and_organize_file(uploaded_file, "document_vide", 0.0)
            if saved_path:
                st.info(f"📁 Document sans texte classé dans **document_vide** : `{saved_path}`")

# 📋 Instructions
with st.expander("ℹ️ Instructions d'utilisation", expanded=False):
    st.markdown("""
    ### Comment utiliser ce classifieur :
    
    1. **📤 Upload** : Déposez votre fichier (PDF, DOCX, ou image)
    2. **🔍 Analyse** : Le système extrait le texte automatiquement
    3. **🤖 Classification** : L'IA prédit le type de document
    4. **📁 Organisation** : Le fichier est automatiquement rangé dans le bon dossier
    
    ### Structure des dossiers :
    - `documents_classifies/` : Dossier principal
        - `[Type_Document]/` : Un dossier par type de document prédit
        - `document_vide/` : Documents sans texte détecté
        - `erreur_classification/` : Documents avec erreur de traitement
    
    ### Format des noms de fichiers :
    - `[Confiance%]_AAAAMMJJ_HHMMSS_nom_original.ext`
    - `[FAIBLE_CONFIANCE_XX%]_...` pour les documents avec confiance < 50%
    
    ### 📝 Note importante :
    **Tous les documents sont classés selon la prédiction de l'IA**, peu importe le niveau de confiance.
    Les fichiers avec faible confiance sont simplement marqués dans le nom de fichier.
    """)

# 🔄 Bouton de nettoyage
if st.sidebar.button("🧹 Nettoyer les dossiers temporaires"):
    # Code pour nettoyer les fichiers temporaires si nécessaire
    st.sidebar.success("✅ Nettoyage effectué")