# Nettoyage du nom de catégorie pour éviter les caractères spéciaux
import re
def clean_category_name(name):
    # Remplace tout caractère non alphanumérique par '_'
    return re.sub(r'[^\w\-]', '_', name)
import os
import shutil
import pytesseract
import cv2
import joblib
from docx import Document
from pdf2image import convert_from_path
import tempfile
from datetime import datetime

# ⚙️ Configuration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = os.path.join(BASE_DIR, "poppler-24.08.0", "Library", "bin")

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = os.path.dirname(TESSERACT_PATH)

# 📁 Configuration des dossiers de destination
BASE_OUTPUT_DIR = os.path.join(BASE_DIR, "documents_classifies")  # Dossier principal
UNKNOWN_DIR = "non_classifies"  # Pour les documents non identifiés

# Charger modèle IA
MODEL_PATH = os.path.join(BASE_DIR, "data", "model", "doc_classifier.joblib")
model = joblib.load(MODEL_PATH)

def create_directories():
    """Créer les dossiers de destination s'ils n'existent pas"""
    if not os.path.exists(BASE_OUTPUT_DIR):
        os.makedirs(BASE_OUTPUT_DIR)
    
    unknown_path = os.path.join(BASE_OUTPUT_DIR, UNKNOWN_DIR)
    if not os.path.exists(unknown_path):
        os.makedirs(unknown_path)
    
    print(f"✅ Dossier principal créé : {BASE_OUTPUT_DIR}")

def create_category_folder(category):
    """Créer un dossier pour une catégorie spécifique"""
    safe_category = clean_category_name(category)
    category_path = os.path.join(BASE_OUTPUT_DIR, safe_category)
    if not os.path.exists(category_path):
        os.makedirs(category_path)
        print(f"📁 Nouveau dossier créé : {category_path}")
    return category_path

def move_file_to_category(source_path, category, confidence_threshold=50.0):
    """Déplacer le fichier vers le dossier approprié"""
    filename = os.path.basename(source_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Toujours classer selon la prédiction, quel que soit le niveau de confiance
    safe_category = clean_category_name(category)
    destination_dir = create_category_folder(safe_category)
    new_filename = f"[{confidence_threshold:.1f}%]_{timestamp}_{filename}"
    destination_path = os.path.join(destination_dir, new_filename)
    
    try:
        shutil.move(source_path, destination_path)
        print(f"📋 Fichier déplacé : {filename} → {destination_path}")
        return destination_path
    except Exception as e:
        print(f"❌ Erreur lors du déplacement : {e}")
        return None

# OCR depuis image
def ocr_from_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray, lang="fra")

# Texte depuis .docx
def extract_text_from_docx(path):
    try:
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        print(f"❌ Erreur lecture DOCX : {e}")
        return ""

# Texte depuis .pdf
def extract_text_from_pdf(path):
    try:
        pages = convert_from_path(path, dpi=300, poppler_path=POPPLER_PATH)
        text = ""
        for page in pages:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                page.save(f.name, "PNG")
                image = cv2.imread(f.name)
                text += ocr_from_image(image) + "\n"
                os.remove(f.name)
        return text
    except Exception as e:
        print(f"❌ Erreur lecture PDF : {e}")
        return ""

def classify_and_organize_document(file_path, move_file=True):
    """Classifier et organiser un document"""
    print(f"🔍 Traitement : {file_path}")
    
    # Extraire le texte selon le format
    if file_path.endswith(".docx"):
        texte = extract_text_from_docx(file_path)
    elif file_path.endswith(".pdf"):
        texte = extract_text_from_pdf(file_path)
    else:
        print("❌ Format non supporté (PDF ou DOCX uniquement).")
        return None
    
    if not texte.strip():
        print("⚠️ Aucun texte détecté.")
        if move_file:
            return move_file_to_category(file_path, UNKNOWN_DIR, 0.0)
        return None
    
    try:
        # Classification IA
        prediction = model.predict([texte])[0]
        confidence = max(model.predict_proba([texte])[0]) * 100
        
        print(f"📊 Type prédit : {prediction}")
        print(f"🎯 Confiance : {confidence:.2f}%")
        
        # Déplacer le fichier si demandé
        if move_file:
            return move_file_to_category(file_path, prediction, confidence)
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'text_preview': texte[:200] + "..." if len(texte) > 200 else texte
        }
        
    except Exception as e:
        print(f"❌ Erreur de prédiction : {e}")
        if move_file:
            return move_file_to_category(file_path, UNKNOWN_DIR, 0.0)
        return None

def batch_classify_and_organize(input_folder):
    """Traitement par lot avec organisation automatique"""
    create_directories()
    
    if not os.path.exists(input_folder):
        print(f"❌ Le dossier {input_folder} n'existe pas.")
        return
    
    files_processed = 0
    results = []
    
    for filename in os.listdir(input_folder):
        if filename.endswith(('.docx', '.pdf')):
            file_path = os.path.join(input_folder, filename)
            result = classify_and_organize_document(file_path, move_file=True)
            if result:
                results.append((filename, result))
                files_processed += 1
            print("-" * 50)
    
    print(f"\n✅ Traitement terminé : {files_processed} fichiers organisés")
    return results

# 🎯 UTILISATION
if __name__ == "__main__":
    # Créer les dossiers de base
    create_directories()
    
    # Option 1: Traiter un fichier unique
    file_path = "docs_simules/jugement.docx"  # ⚠️ Modifie ce chemin
    if os.path.exists(file_path):
        result = classify_and_organize_document(file_path, move_file=True)
    
    # Option 2: Traitement par lot (décommente pour utiliser)
    # batch_classify_and_organize("docs_simules")