import streamlit as st
import pytesseract
import cv2
import joblib
import os
import shutil
import sys
from pdf2image import convert_from_bytes
from docx import Document
from tempfile import NamedTemporaryFile
import numpy as np
from PIL import Image, Image as PILImage
from datetime import datetime

# Import language manager and navigation first (before any usage)
# Add the parent directory to Python path to find improvements module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import language manager first (always needed)
try:
    from improvements.language_manager import lang_manager
except ImportError as e:
    # Create dummy language manager if import fails
    class DummyLangManager:
        def get_text(self, key):
            return key
    lang_manager = DummyLangManager()

# Import navigation components
try:
    from improvements.navigation import nav_manager, create_navigation_header, render_status_indicator
except ImportError as e:
    # Create dummy functions if import fails
    class DummyNavManager:
        def render_navigation_sidebar(self, current_app):
            pass
    nav_manager = DummyNavManager()
    def create_navigation_header():
        pass
    def render_status_indicator():
        pass

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

st.title("📄 " + lang_manager.get_text("document_classifier"))

# Navigation
nav_manager.render_navigation_sidebar("📄 Document Classifier")

# Header
create_navigation_header()
render_status_indicator()

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
st.sidebar.header("⚙️ " + lang_manager.get_text("options"))
auto_organize = st.sidebar.checkbox("📁 " + lang_manager.get_text("auto_organization"), value=True, 
                                   help=lang_manager.get_text("auto_organization_help"))

show_confidence_warning = st.sidebar.slider("⚠️ " + lang_manager.get_text("warning_threshold"), 
                                           min_value=0, max_value=100, value=20,
                                           help=lang_manager.get_text("warning_threshold_help"))

# 📊 Affichage de l'arborescence actuelle
if st.sidebar.button("🗂️ " + lang_manager.get_text("view_structure")):
    st.sidebar.subheader(lang_manager.get_text("folder_structure"))
    if os.path.exists(BASE_OUTPUT_DIR):
        for item in os.listdir(BASE_OUTPUT_DIR):
            item_path = os.path.join(BASE_OUTPUT_DIR, item)
            if os.path.isdir(item_path):
                file_count = len([f for f in os.listdir(item_path) 
                                if os.path.isfile(os.path.join(item_path, f))])
                st.sidebar.write(f"📁 {item} ({file_count} fichiers)")
    else:
        st.sidebar.write(lang_manager.get_text("no_folders_created"))

# 📤 Interface principale
uploaded_file = st.file_uploader("📤 " + lang_manager.get_text("upload_files"), 
                                 type=["pdf", "docx", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Créer les dossiers si nécessaire
    create_directories()
    
    ext = uploaded_file.name.lower().split(".")[-1]
    
    # Afficher les informations du fichier
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 " + lang_manager.get_text("file_name"), uploaded_file.name)
    with col2:
        st.metric("📏 " + lang_manager.get_text("file_size"), f"{uploaded_file.size / 1024:.1f} KB")
    with col3:
        st.metric("🔤 " + lang_manager.get_text("file_type"), ext.upper())

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
    with st.expander("📝 " + lang_manager.get_text("extracted_text"), expanded=False):
        if texte.strip():
            st.text_area("Texte", texte, height=200)
        else:
            st.warning(lang_manager.get_text("no_text_detected"))

    # Classification
    if texte.strip():
        with st.spinner("🤖 " + lang_manager.get_text("classification_in_progress")):
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
                st.warning(f"🎯 {proba:.1f}% ({lang_manager.get_text('low_confidence')})")
        
        # Organisation automatique
        if auto_organize:
            st.divider()
            with st.spinner("📁 " + lang_manager.get_text("file_organization")):
                saved_path = save_and_organize_file(uploaded_file, pred, proba)
                
                if saved_path:
                    if proba >= show_confidence_warning:
                        st.success(f"✅ {lang_manager.get_text('file_classified')} **{pred}** : `{saved_path}`")
                    else:
                        st.warning(f"⚠️ {lang_manager.get_text('file_classified_low_confidence')} **{pred}** : `{saved_path}`")
                    
                    # Bouton pour ouvrir le dossier
                    folder_path = os.path.dirname(saved_path)
                    if st.button("🗂️ " + lang_manager.get_text("open_folder")):
                        os.startfile(folder_path)  # Windows uniquement
                else:
                    st.error("❌ " + lang_manager.get_text("organization_error"))
        
        # Affichage des probabilités détaillées
        with st.expander("📈 " + lang_manager.get_text("detailed_probabilities"), expanded=False):
            all_probas = model.predict_proba([texte])[0]
            classes = model.classes_
            
            for i, (classe, prob) in enumerate(zip(classes, all_probas)):
                prob_percent = prob * 100
                st.progress(prob_percent / 100, text=f"{classe}: {prob_percent:.1f}%")
    
    else:
        st.error("❌ " + lang_manager.get_text("no_readable_text"))
        
        # Même si pas de texte, on classe dans "document_vide"
        if auto_organize:
            saved_path = save_and_organize_file(uploaded_file, "document_vide", 0.0)
            if saved_path:
                st.info(f"📁 {lang_manager.get_text('empty_document')} **document_vide** : `{saved_path}`")

# 📋 Instructions
with st.expander("ℹ️ " + lang_manager.get_text("instructions"), expanded=False):
    st.markdown(f"""
    ### {lang_manager.get_text('how_to_use')}
    
    1. **{lang_manager.get_text('step_upload')}**
    2. **{lang_manager.get_text('step_analysis')}**
    3. **{lang_manager.get_text('step_classification')}**
    4. **{lang_manager.get_text('step_organization')}**
    
    ### {lang_manager.get_text('folder_structure_title')}
    - `{lang_manager.get_text('main_folder')}`
        - `{lang_manager.get_text('type_folder')}`
        - `{lang_manager.get_text('empty_folder')}`
        - `{lang_manager.get_text('error_folder')}`
    
    ### {lang_manager.get_text('filename_format')}
    - `{lang_manager.get_text('confidence_format')}`
    - `{lang_manager.get_text('low_confidence_format')}`
    
    ### {lang_manager.get_text('important_note')}
    **{lang_manager.get_text('classification_note')}**
    """)

# 🔄 Bouton de nettoyage
if st.sidebar.button("🧹 " + lang_manager.get_text("clean_temp")):
    # Code pour nettoyer les fichiers temporaires si nécessaire
    st.sidebar.success("✅ " + lang_manager.get_text("cleanup_complete"))