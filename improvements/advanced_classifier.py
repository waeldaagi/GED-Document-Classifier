import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import warnings
warnings.filterwarnings('ignore')

class AdvancedDocumentClassifier:
    def __init__(self):
        self.models = {}
        self.ensemble_model = None
        self.vectorizer = None
        self.calibrated_model = None
        self.french_stop_words = self._get_french_stop_words()
    
    def _get_french_stop_words(self):
        """Get French stop words list"""
        return [
            'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou', 'mais', 'donc',
            'car', 'ni', 'or', 'puis', 'ensuite', 'alors', 'par', 'pour', 'avec',
            'sans', 'sous', 'sur', 'dans', 'entre', 'parmi', 'vers', 'envers', 'contre',
            'selon', 'malgré', 'en', 'à', 'au', 'aux',
            'ce', 'cette', 'ces', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses',
            'notre', 'votre', 'leur', 'leurs', 'qui', 'que', 'quoi', 'dont', 'où', 'quand',
            'comment', 'pourquoi', 'combien', 'quel', 'quelle', 'quels', 'quelles',
            'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'me', 'te', 'se',
            'lui', 'y', 'en', 'ceci', 'cela', 'ça', 'celui', 'celle', 'ceux', 'celles',
            'être', 'avoir', 'faire', 'dire', 'aller', 'voir', 'savoir', 'pouvoir', 'vouloir',
            'devoir', 'falloir', 'valoir', 'paraître', 'sembler', 'rester', 'devenir',
            'parce', 'comme', 'si', 'sinon', 'sauf', 'excepté',
            'hormis', 'outre', 'devant', 'derrière',
            'avant', 'après', 'pendant', 'durant', 'depuis', 'vers',
            'mais', 'ses', 'pouvoir', 'quoi', 'falloir', 'celui', 'lui', 'sinon', 'avant',
            'me', 'à', 'leur', 'ils', 'dont', 'sur'
        ]
        
    def create_advanced_pipeline(self):
        """Create an ensemble of multiple models for better performance"""
        
        # TF-IDF Vectorizer with better parameters
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.95,
            stop_words=self.french_stop_words
        )
        
        # Multiple base models
        nb_model = MultinomialNB(alpha=0.1)
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        svm_model = SVC(kernel='rbf', probability=True, random_state=42)
        
        # Create ensemble
        self.ensemble_model = VotingClassifier(
            estimators=[
                ('nb', nb_model),
                ('rf', rf_model),
                ('svm', svm_model)
            ],
            voting='soft'
        )
        
        # Calibrate the ensemble for better confidence scores
        self.calibrated_model = CalibratedClassifierCV(
            self.ensemble_model, 
            cv=5, 
            method='isotonic'
        )
        
    def train_advanced_model(self, data_path):
        """Train the advanced ensemble model"""
        print("🚀 Training Advanced Ensemble Model...")
        
        # Load data
        df = pd.read_csv(data_path)
        X = df['texte']
        y = df['label']
        
        # Create pipeline
        self.create_advanced_pipeline()
        
        # Transform text
        X_transformed = self.vectorizer.fit_transform(X)
        
        # Train calibrated ensemble
        self.calibrated_model.fit(X_transformed, y)
        
        # Cross-validation
        cv_scores = cross_val_score(self.calibrated_model, X_transformed, y, cv=5)
        print(f"✅ Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Save model
        self.save_model()
        
    def predict_with_confidence(self, text):
        """Predict with calibrated confidence scores"""
        X_transformed = self.vectorizer.transform([text])
        prediction = self.calibrated_model.predict(X_transformed)[0]
        probabilities = self.calibrated_model.predict_proba(X_transformed)[0]
        confidence = max(probabilities) * 100
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'probabilities': dict(zip(self.calibrated_model.classes_, probabilities))
        }
    
    def save_model(self):
        """Save the trained model"""
        model_data = {
            'vectorizer': self.vectorizer,
            'calibrated_model': self.calibrated_model,
            'classes': self.calibrated_model.classes_
        }
        joblib.dump(model_data, 'data/model/advanced_classifier.joblib')
        print("✅ Advanced model saved successfully!")
    
    def load_model(self):
        """Load the trained model"""
        model_data = joblib.load('data/model/advanced_classifier.joblib')
        self.vectorizer = model_data['vectorizer']
        self.calibrated_model = model_data['calibrated_model']
        print("✅ Advanced model loaded successfully!")

# Usage example
if __name__ == "__main__":
    classifier = AdvancedDocumentClassifier()
    classifier.train_advanced_model("data/dataset.csv")
    
    # Test prediction
    test_text = "Le présent contrat est conclu pour une durée de deux ans entre les parties."
    result = classifier.predict_with_confidence(test_text)
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']:.2f}%")
