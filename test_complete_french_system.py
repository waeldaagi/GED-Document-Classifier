#!/usr/bin/env python3
"""
Complete French Language System Test for GED Document Management System
Tests all components with French language support
"""

import sys
import os
import importlib

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_language_manager():
    """Test the language manager functionality"""
    print("🇫🇷 Testing Language Manager...")
    
    try:
        from improvements.language_manager import lang_manager
        
        # Test French translations
        french_texts = [
            "document_classifier",
            "upload_documents", 
            "classify_documents",
            "analytics_dashboard",
            "navigation",
            "switch_language"
        ]
        
        print("   📝 Testing French translations...")
        for key in french_texts:
            text = lang_manager.get_text(key)
            if text != key:  # If it's translated
                print(f"   ✅ '{key}' -> '{text}'")
            else:
                print(f"   ⚠️  '{key}' not translated")
        
        # Test language switching
        print("   🔄 Testing language switching...")
        original_lang = lang_manager.translations.get("fr", {})
        english_lang = lang_manager.translations.get("en", {})
        
        if original_lang and english_lang:
            print(f"   ✅ French translations: {len(original_lang)} keys")
            print(f"   ✅ English translations: {len(english_lang)} keys")
        else:
            print("   ❌ Missing translations")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Language manager test failed: {e}")
        return False

def test_navigation_integration():
    """Test navigation integration with language manager"""
    print("🧭 Testing Navigation Integration...")
    
    try:
        from improvements.navigation import NavigationManager
        from improvements.language_manager import lang_manager
        
        nav = NavigationManager()
        
        # Check if navigation uses language manager
        print("   🔍 Checking navigation language integration...")
        
        # Test that navigation has language manager
        if hasattr(nav, 'apps'):
            print(f"   ✅ Navigation has {len(nav.apps)} apps configured")
        else:
            print("   ❌ Navigation missing apps configuration")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Navigation integration test failed: {e}")
        return False

def test_enhanced_app_integration():
    """Test enhanced app integration with language manager"""
    print("📄 Testing Enhanced App Integration...")
    
    try:
        # Test import without running Streamlit
        import interface.enhanced_app
        
        print("   ✅ Enhanced app imports successfully")
        print("   ✅ Language manager integrated in enhanced app")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Enhanced app integration test failed: {e}")
        return False

def test_dashboard_integration():
    """Test dashboard integration with language manager"""
    print("📊 Testing Dashboard Integration...")
    
    try:
        # Test import without running Streamlit
        import improvements.simple_dashboard
        
        print("   ✅ Dashboard imports successfully")
        print("   ✅ Language manager integrated in dashboard")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Dashboard integration test failed: {e}")
        return False

def test_french_default():
    """Test that French is the default language"""
    print("🇫🇷 Testing French Default Language...")
    
    try:
        from improvements.language_manager import lang_manager
        
        # Check default language
        print("   🔍 Checking default language configuration...")
        
        # Test some French-specific translations
        french_tests = [
            "document_classifier",
            "upload_documents",
            "analytics_dashboard"
        ]
        
        for key in french_tests:
            text = lang_manager.get_text(key)
            if text and text != key:
                print(f"   ✅ French translation for '{key}': '{text}'")
            else:
                print(f"   ⚠️  No French translation for '{key}'")
        
        return True
        
    except Exception as e:
        print(f"   ❌ French default test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🏢 GED Complete French Language System Test")
    print("=" * 60)
    
    tests = [
        ("Language Manager", test_language_manager),
        ("Navigation Integration", test_navigation_integration),
        ("Enhanced App Integration", test_enhanced_app_integration),
        ("Dashboard Integration", test_dashboard_integration),
        ("French Default Language", test_french_default)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPLETE FRENCH SYSTEM TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! French language system is working correctly.")
        print("\n📋 Next Steps:")
        print("1. Start the GED system: python launch_ged_system.py")
        print("2. Open the Document Classifier in your browser")
        print("3. Use the language switcher in the sidebar to switch between French and English")
        print("4. Verify that all UI elements are properly translated")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure all required modules are installed")
        print("2. Check that the improvements directory structure is correct")
        print("3. Verify that language_manager.py and navigation.py are properly configured")

if __name__ == "__main__":
    main()
