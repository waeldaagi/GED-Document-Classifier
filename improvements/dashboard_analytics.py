import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os
import json
from typing import Dict, List
import sqlite3

class DocumentAnalytics:
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT,
                document_count INTEGER,
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
    
    def get_trends_data(self, days=30):
        """Get time series trends"""
        conn = sqlite3.connect(self.db_path)
        
        trends = pd.read_sql_query(f'''
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as documents_processed,
                AVG(confidence) as avg_confidence,
                AVG(processing_time) as avg_time
            FROM document_processing
            WHERE timestamp >= datetime('now', '-{days} days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', conn)
        
        conn.close()
        return trends

class AnalyticsDashboard:
    def __init__(self):
        self.analytics = DocumentAnalytics()
    
    def render_dashboard(self):
        """Render the main analytics dashboard"""
        st.set_page_config(page_title="GED Analytics Dashboard", layout="wide")
        
        st.title("📊 GED Document Analytics Dashboard")
        
        # Sidebar filters
        st.sidebar.header("📅 Filters")
        days_filter = st.sidebar.selectbox("Time Period", [7, 30, 90, 365], index=1)
        
        # Get data
        recent_data, overall_stats = self.analytics.get_processing_stats(days_filter)
        distribution = self.analytics.get_document_type_distribution()
        trends = self.analytics.get_trends_data(days_filter)
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📄 Total Documents",
                f"{overall_stats['total_documents'].iloc[0]:,}",
                f"+{len(recent_data)} this period"
            )
        
        with col2:
            avg_conf = overall_stats['avg_confidence'].iloc[0]
            st.metric(
                "🎯 Avg Confidence",
                f"{avg_conf:.1f}%" if not pd.isna(avg_conf) else "N/A"
            )
        
        with col3:
            avg_time = overall_stats['avg_processing_time'].iloc[0]
            st.metric(
                "⏱️ Avg Processing Time",
                f"{avg_time:.2f}s" if not pd.isna(avg_time) else "N/A"
            )
        
        with col4:
            total_size = overall_stats['total_size_mb'].iloc[0]
            st.metric(
                "💾 Total Size",
                f"{total_size/1024/1024:.1f} GB" if not pd.isna(total_size) else "N/A"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_document_distribution(distribution)
        
        with col2:
            self.render_confidence_distribution(recent_data)
        
        # Trends
        st.subheader("📈 Processing Trends")
        self.render_trends_chart(trends)
        
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_processing_performance(recent_data)
        
        with col2:
            self.render_error_analysis(recent_data)
    
    def render_document_distribution(self, distribution):
        """Render document type distribution chart"""
        st.subheader("📊 Document Type Distribution")
        
        if not distribution.empty:
            fig = px.pie(
                distribution, 
                values='count', 
                names='document_type',
                title="Documents by Type"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for document distribution")
    
    def render_confidence_distribution(self, data):
        """Render confidence distribution chart"""
        st.subheader("🎯 Confidence Distribution")
        
        if not data.empty and 'confidence' in data.columns:
            fig = px.histogram(
                data, 
                x='confidence',
                nbins=20,
                title="Confidence Score Distribution"
            )
            fig.update_layout(xaxis_title="Confidence (%)", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No confidence data available")
    
    def render_trends_chart(self, trends):
        """Render time series trends"""
        if not trends.empty:
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Documents Processed', 'Average Confidence'),
                vertical_spacing=0.1
            )
            
            # Documents processed
            fig.add_trace(
                go.Scatter(x=trends['date'], y=trends['documents_processed'], 
                          mode='lines+markers', name='Documents'),
                row=1, col=1
            )
            
            # Average confidence
            fig.add_trace(
                go.Scatter(x=trends['date'], y=trends['avg_confidence'], 
                          mode='lines+markers', name='Confidence'),
                row=2, col=1
            )
            
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trends data available")
    
    def render_processing_performance(self, data):
        """Render processing performance metrics"""
        st.subheader("⚡ Processing Performance")
        
        if not data.empty and 'processing_time' in data.columns:
            # Processing time by document type
            perf_by_type = data.groupby('document_type')['processing_time'].agg(['mean', 'count']).reset_index()
            
            fig = px.bar(
                perf_by_type,
                x='document_type',
                y='mean',
                title="Average Processing Time by Document Type"
            )
            fig.update_layout(xaxis_title="Document Type", yaxis_title="Time (seconds)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No performance data available")
    
    def render_error_analysis(self, data):
        """Render error analysis"""
        st.subheader("⚠️ Error Analysis")
        
        if not data.empty and 'status' in data.columns:
            error_counts = data['status'].value_counts()
            
            fig = px.pie(
                values=error_counts.values,
                names=error_counts.index,
                title="Processing Status Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No error data available")

# Business Intelligence Functions
class BusinessIntelligence:
    def __init__(self, analytics):
        self.analytics = analytics
    
    def calculate_efficiency_metrics(self):
        """Calculate business efficiency metrics"""
        conn = sqlite3.connect(self.analytics.db_path)
        
        # Calculate metrics
        metrics = pd.read_sql_query('''
            SELECT 
                COUNT(*) as total_docs,
                COUNT(CASE WHEN confidence >= 80 THEN 1 END) as high_confidence_docs,
                COUNT(CASE WHEN confidence < 50 THEN 1 END) as low_confidence_docs,
                AVG(processing_time) as avg_time,
                SUM(file_size) as total_size
            FROM document_processing
        ''', conn)
        
        conn.close()
        
        if not metrics.empty:
            total = metrics['total_docs'].iloc[0]
            high_conf = metrics['high_confidence_docs'].iloc[0]
            low_conf = metrics['low_confidence_docs'].iloc[0]
            
            return {
                'accuracy_rate': (high_conf / total * 100) if total > 0 else 0,
                'error_rate': (low_conf / total * 100) if total > 0 else 0,
                'avg_processing_time': metrics['avg_time'].iloc[0],
                'total_storage_gb': metrics['total_size'].iloc[0] / (1024**3) if metrics['total_size'].iloc[0] else 0
            }
        
        return {}
    
    def generate_insights(self):
        """Generate business insights"""
        insights = []
        
        # Get recent data
        recent_data, _ = self.analytics.get_processing_stats(7)
        
        if not recent_data.empty:
            # Document type insights
            doc_counts = recent_data['document_type'].value_counts()
            if not doc_counts.empty:
                most_common = doc_counts.index[0]
                insights.append(f"📄 Most processed document type: {most_common} ({doc_counts.iloc[0]} documents)")
            
            # Confidence insights
            if 'confidence' in recent_data.columns:
                avg_conf = recent_data['confidence'].mean()
                if avg_conf < 70:
                    insights.append("⚠️ Average confidence is below 70% - consider model retraining")
                elif avg_conf > 90:
                    insights.append("✅ Excellent confidence scores - model performing well")
            
            # Processing time insights
            if 'processing_time' in recent_data.columns:
                avg_time = recent_data['processing_time'].mean()
                if avg_time > 10:
                    insights.append("🐌 Processing time is high - consider optimization")
                elif avg_time < 2:
                    insights.append("⚡ Fast processing - system performing efficiently")
        
        return insights

# Usage
if __name__ == "__main__":
    dashboard = AnalyticsDashboard()
    dashboard.render_dashboard()
