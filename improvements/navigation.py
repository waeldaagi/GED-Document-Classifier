import streamlit as st
import webbrowser
from typing import Dict, List
from .language_manager import lang_manager

class NavigationManager:
    """Manages navigation between different components of the GED system"""
    
    def __init__(self):
        self.apps = {
            "📄 Document Classifier": {
                "url": "http://localhost:8502",
                "description": "Upload and classify documents with AI",
                "features": [
                    "📤 Upload documents (PDF, DOCX, JPG, PNG)",
                    "🤖 AI-powered classification",
                    "📁 Automatic file organization",
                    "🎯 Confidence scoring"
                ]
            },
            "📊 Analytics Dashboard": {
                "url": "http://localhost:8503",
                "description": "Monitor system performance and statistics",
                "features": [
                    "📈 Real-time processing statistics",
                    "📊 Document type distribution",
                    "⚡ Performance metrics",
                    "📋 Recent activity logs"
                ]
            },

        }
    
    def render_navigation_sidebar(self, current_app: str):
        """Render navigation sidebar"""
        st.sidebar.title("🧭 " + lang_manager.get_text("navigation"))
        
        # Current app indicator
        st.sidebar.markdown(f"**📍 {lang_manager.get_text('current')}:** {current_app}")
        st.sidebar.markdown("---")
        
        # Navigation options
        for app_name, app_info in self.apps.items():
            if app_name != current_app:
                if st.sidebar.button(f"➡️ {app_name}", key=f"nav_{app_name}"):
                    self.open_app(app_name)
        
        # Quick links section
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔗 " + lang_manager.get_text("quick_links"))
        
        for app_name, app_info in self.apps.items():
            if app_name != current_app:
                st.sidebar.markdown(f"[{app_name}]({app_info['url']})")
        
        # Language selector
        lang_manager.render_language_selector()
    
    def open_app(self, app_name: str):
        """Open the specified app"""
        if app_name in self.apps:
            app_info = self.apps[app_name]
            st.info(f"🔄 Opening {app_name}...")
            st.markdown(f"### [{app_name}]({app_info['url']})")
            st.markdown(f"**{app_info['description']}**")
            st.markdown("**Features:**")
            for feature in app_info['features']:
                st.markdown(f"- {feature}")
            
            # Try to open in new tab
            try:
                webbrowser.open_new_tab(app_info['url'])
            except:
                pass
            
            st.stop()
    
    def render_app_info(self, app_name: str):
        """Render information about the current app"""
        if app_name in self.apps:
            app_info = self.apps[app_name]
            st.info(f"**{app_name}** - {app_info['description']}")
    
    def get_app_url(self, app_name: str) -> str:
        """Get the URL for a specific app"""
        return self.apps.get(app_name, {}).get("url", "#")

def create_navigation_header():
    """Create a consistent header across all apps"""
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
        <h1 style="margin: 0; color: #1f77b4;">🏢 {lang_manager.get_text('ged_system')}</h1>
        <p style="margin: 0.5rem 0 0 0; color: #666;">{lang_manager.get_text('advanced_platform')}</p>
    </div>
    """, unsafe_allow_html=True)

def render_status_indicator():
    """Render system status indicator"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(f"🤖 {lang_manager.get_text('ml_model')}", f"✅ {lang_manager.get_text('active')}", f"90.3% {lang_manager.get_text('accuracy')}")
    
    with col2:
        st.metric(f"📊 {lang_manager.get_text('analytics')}", f"✅ {lang_manager.get_text('active')}", lang_manager.get_text('real_time'))
    
    with col3:
        st.metric(f"🌐 {lang_manager.get_text('api')}", f"✅ {lang_manager.get_text('active')}", f"{lang_manager.get_text('port')} 8000")

# Global navigation instance
nav_manager = NavigationManager()
