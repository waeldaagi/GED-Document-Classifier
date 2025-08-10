import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import sys
from typing import Dict, List
import sqlite3

# Import language manager and navigation first (before any usage)
# Add the current directory to Python path to find modules
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

class SimpleDocumentAnalytics:
    def __init__(self, db_path="data/analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_processing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                document_type TEXT,
                confidence REAL,
                processing_time REAL,
                file_size INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                error_message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_document_processing(self, filename, doc_type, confidence, processing_time, file_size, status="success", error_msg=None):
        """Log document processing event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO document_processing 
            (filename, document_type, confidence, processing_time, file_size, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (filename, doc_type, confidence, processing_time, file_size, status, error_msg))
        
        conn.commit()
        conn.close()
    
    def get_processing_stats(self, days=30):
        """Get processing statistics"""
        conn = sqlite3.connect(self.db_path)
        
        # Recent processing data
        recent_data = pd.read_sql_query(f'''
            SELECT * FROM document_processing 
            WHERE timestamp >= datetime('now', '-{days} days')
        ''', conn)
        
        # Overall stats
        overall_stats = pd.read_sql_query('''
            SELECT 
                COUNT(*) as total_documents,
                AVG(confidence) as avg_confidence,
                AVG(processing_time) as avg_processing_time,
                SUM(file_size) as total_size_mb
            FROM document_processing
        ''', conn)
        
        conn.close()
        
        return recent_data, overall_stats
    
    def get_document_type_distribution(self):
        """Get document type distribution"""
        conn = sqlite3.connect(self.db_path)
        
        distribution = pd.read_sql_query('''
            SELECT 
                document_type,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence,
                AVG(processing_time) as avg_time
            FROM document_processing
            GROUP BY document_type
            ORDER BY count DESC
        ''', conn)
        
        conn.close()
        return distribution

class SimpleAnalyticsDashboard:
    def __init__(self):
        self.analytics = SimpleDocumentAnalytics()
    
    def render_dashboard(self):
        """Render the main analytics dashboard"""
        st.set_page_config(page_title="GED Analytics Dashboard", layout="wide")
        
        st.title("📊 " + lang_manager.get_text("analytics_dashboard"))
        st.info("🔧 " + lang_manager.get_text("monitor_performance"))
        
        # Navigation
        nav_manager.render_navigation_sidebar("📊 Analytics Dashboard")
        
        # Header
        create_navigation_header()
        render_status_indicator()
        
        # Sidebar filters
        st.sidebar.header("📅 " + lang_manager.get_text("filters"))
        days_filter = st.sidebar.selectbox(lang_manager.get_text("time_period"), [7, 30, 90, 365], index=1)
        
        # Get data
        recent_data, overall_stats = self.analytics.get_processing_stats(days_filter)
        distribution = self.analytics.get_document_type_distribution()
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_docs = overall_stats['total_documents'].iloc[0] if not overall_stats.empty else 0
            st.metric(
                "📄 " + lang_manager.get_text("total_documents"),
                f"{total_docs:,}",
                f"+{len(recent_data)} this period"
            )
        
        with col2:
            avg_conf = overall_stats['avg_confidence'].iloc[0] if not overall_stats.empty else None
            st.metric(
                "🎯 " + lang_manager.get_text("avg_confidence"),
                f"{avg_conf:.1f}%" if avg_conf and avg_conf > 0 else "N/A"
            )
        
        with col3:
            avg_time = overall_stats['avg_processing_time'].iloc[0] if not overall_stats.empty else None
            st.metric(
                "⏱️ " + lang_manager.get_text("avg_processing_time"),
                f"{avg_time:.2f}s" if avg_time and avg_time > 0 else "N/A"
            )
        
        with col4:
            total_size = overall_stats['total_size_mb'].iloc[0] if not overall_stats.empty else None
            st.metric(
                "💾 " + lang_manager.get_text("total_size"),
                f"{total_size/1024/1024:.1f} GB" if total_size and total_size > 0 else "N/A"
            )
        
        # Document Distribution
        st.subheader("📊 " + lang_manager.get_text("document_type_distribution"))
        if not distribution.empty:
            st.dataframe(distribution, use_container_width=True)
            
            # Simple bar chart using st.bar_chart
            chart_data = distribution.set_index('document_type')['count']
            st.bar_chart(chart_data)
        else:
            st.info(lang_manager.get_text("no_data_available"))
        
        # Recent Activity
        st.subheader("📈 " + lang_manager.get_text("recent_activity"))
        if not recent_data.empty:
            # Show recent documents
            recent_display = recent_data[['filename', 'document_type', 'confidence', 'processing_time', 'timestamp']].head(10)
            st.dataframe(recent_display, use_container_width=True)
        else:
            st.info(lang_manager.get_text("no_data_available"))
        
        # Performance Metrics
        st.subheader("⚡ " + lang_manager.get_text("performance_overview"))
        col1, col2 = st.columns(2)
        
        with col1:
            if not recent_data.empty and 'processing_time' in recent_data.columns:
                st.write(f"**{lang_manager.get_text('processing_time_by_type')}:**")
                perf_by_type = recent_data.groupby('document_type')['processing_time'].agg(['mean', 'count']).reset_index()
                st.dataframe(perf_by_type, use_container_width=True)
            else:
                st.info(lang_manager.get_text("no_data_available"))
        
        with col2:
            if not recent_data.empty and 'confidence' in recent_data.columns:
                st.write(f"**{lang_manager.get_text('confidence_distribution')}:**")
                conf_stats = recent_data['confidence'].describe()
                st.dataframe(conf_stats.to_frame(), use_container_width=True)
            else:
                st.info(lang_manager.get_text("no_data_available"))
        
        # Add some sample data for testing
        if st.button(lang_manager.get_text("add_sample_data")):
            self.add_sample_data()
            st.success(lang_manager.get_text("sample_data_added"))
    
    def add_sample_data(self):
        """Add sample data for testing"""
        sample_data = [
            ("contrat_001.pdf", "contrat", 95.5, 2.3, 1024000, "success"),
            ("facture_001.pdf", "facture", 88.2, 1.8, 512000, "success"),
            ("jugement_001.pdf", "jugement", 92.1, 3.1, 2048000, "success"),
            ("attestation_001.pdf", "attestation", 87.5, 1.5, 256000, "success"),
            ("demande_stage_001.pdf", "demande_stage", 91.3, 2.7, 768000, "success"),
            ("demande_conge_001.pdf", "demande_conge", 89.7, 2.1, 384000, "success"),
        ]
        
        for filename, doc_type, confidence, processing_time, file_size, status in sample_data:
            self.analytics.log_document_processing(
                filename, doc_type, confidence, processing_time, file_size, status
            )

if __name__ == "__main__":
    dashboard = SimpleAnalyticsDashboard()
    dashboard.render_dashboard()
