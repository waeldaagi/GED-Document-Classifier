#!/usr/bin/env python3
"""
Comprehensive Test Script for GED Document Classifier
Tests all major components of the improved system
"""

import sys
import os
import time
import traceback

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        from sklearn.ensemble import RandomForestClassifier, VotingClassifier
        print("✅ scikit-learn imported successfully")
    except ImportError as e:
        print(f"❌ scikit-learn import failed: {e}")
        return False
    
    try:
        import joblib
        print("✅ joblib imported successfully")
    except ImportError as e:
        print(f"❌ joblib import failed: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ plotly imported successfully")
    except ImportError as e:
        print(f"❌ plotly import failed: {e}")
        print("⚠️  Note: Using simplified dashboard instead")
    
    return True

def test_advanced_classifier():
    """Test the advanced classifier"""
    print("\n🧠 Testing Advanced Classifier...")
    
    try:
        from improvements.advanced_classifier import AdvancedDocumentClassifier
        
        # Test classifier initialization
        classifier = AdvancedDocumentClassifier()
        print("✅ Advanced classifier initialized")
        
        # Test if model file exists
        model_path = "data/model/advanced_classifier.joblib"
        if os.path.exists(model_path):
            print("✅ Advanced model file found")
            
            # Test model loading
            classifier.load_model()
            print("✅ Advanced model loaded successfully")
            
            # Test prediction
            test_text = "Le présent contrat est conclu pour une durée de deux ans entre les parties."
            result = classifier.predict_with_confidence(test_text)
            print(f"✅ Prediction test: {result['prediction']} (confidence: {result['confidence']:.1f}%)")
            
        else:
            print("⚠️  Advanced model file not found - training new model...")
            classifier.train_advanced_model("data/dataset.csv")
            print("✅ Advanced model trained and saved")
            
        return True
        
    except Exception as e:
        print(f"❌ Advanced classifier test failed: {e}")
        traceback.print_exc()
        return False

def test_enhanced_ocr():
    """Test the enhanced OCR system"""
    print("\n👁️  Testing Enhanced OCR...")
    
    try:
        from improvements.enhanced_ocr import EnhancedOCR
        
        # Test OCR initialization
        ocr = EnhancedOCR()
        print("✅ Enhanced OCR initialized")
        
        # Test structured data extraction
        test_text = "Contrat signé le 15/03/2024 pour un montant de 5000€. Contact: john@example.com"
        structured_data = ocr.extract_structured_data(test_text)
        print(f"✅ Structured data extraction: {len(structured_data['dates'])} dates, {len(structured_data['amounts'])} amounts found")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced OCR test failed: {e}")
        traceback.print_exc()
        return False

def test_analytics():
    """Test the analytics system"""
    print("\n📊 Testing Analytics System...")
    
    try:
        from improvements.simple_dashboard import SimpleDocumentAnalytics
        
        # Test analytics initialization
        analytics = SimpleDocumentAnalytics()
        print("✅ Analytics system initialized")
        
        # Test logging
        analytics.log_document_processing(
            "test_doc.pdf", "contrat", 95.5, 2.3, 1024000, "success"
        )
        print("✅ Document processing logged")
        
        # Test stats retrieval
        recent_data, overall_stats = analytics.get_processing_stats(7)
        print(f"✅ Analytics stats retrieved: {len(recent_data)} recent documents")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
        traceback.print_exc()
        return False

def test_api_server():
    """Test the API server components"""
    print("\n🌐 Testing API Server Components...")
    
    try:
        # Test FastAPI import
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
        
        # Test API models
        from pydantic import BaseModel
        print("✅ Pydantic models imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Test file structure and data"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        "data/dataset.csv",
        "requirements.txt",
        "interface/enhanced_app.py",
        "classify/classifier_with_organizer.py"
    ]
    
    required_dirs = [
        "data",
        "data/model",
        "documents_classifies",
        "docs_simules",
        "interface",
        "classify",
        "improvements"
    ]
    
    all_good = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_good = False
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/ directory exists")
        else:
            print(f"❌ {dir_path}/ directory missing")
            all_good = False
    
    return all_good

def test_data_quality():
    """Test data quality"""
    print("\n📊 Testing Data Quality...")
    
    try:
        import pandas as pd
        
        # Test dataset
        if os.path.exists("data/dataset.csv"):
            df = pd.read_csv("data/dataset.csv")
            print(f"✅ Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
            print(f"✅ Document types: {df['label'].value_counts().to_dict()}")
        else:
            print("⚠️  Dataset file not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive GED System Tests...")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Data Quality", test_data_quality),
        ("Advanced Classifier", test_advanced_classifier),
        ("Enhanced OCR", test_enhanced_ocr),
        ("Analytics System", test_analytics),
        ("API Server Components", test_api_server),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Your GED system is ready to use!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
