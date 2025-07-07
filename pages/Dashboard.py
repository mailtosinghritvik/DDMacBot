import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# Set page configuration
st.set_page_config(
    page_title="Dashboard - AccuBid Converter",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #1f4e79;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .file-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
    }
    
    .file-item:hover {
        background: #e9ecef;
        cursor: pointer;
    }
    
    .integration-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    
    .template-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    
    .status-active { color: #28a745; font-weight: bold; }
    .status-inactive { color: #6c757d; }
    .status-error { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'project_history' not in st.session_state:
    st.session_state.project_history = [
        {
            "company_name": "ABC Electrical Contractors",
            "project_name": "Downtown Office Complex Phase 2",
            "project_type": "Commercial",
            "upload_date": datetime.now() - timedelta(hours=2),
            "status": "AI Enhanced",
            "file_size": "2.3 MB",
            "processing_time": "4.7s",
            "outputs": ["Enhanced Markdown", "RAG Vector Store", "Dashboard Entry"],
            "ai_summary": "Large commercial electrical project with advanced lighting systems, power distribution, and security integration. Estimated 240 hours of labor with $89,450 total project cost.",
            "vector_store_id": "file_abc123xyz",
            "location": "Seattle, WA"
        },
        {
            "company_name": "Residential Plus Electric", 
            "project_name": "Luxury Home Complex A",
            "project_type": "Residential",
            "upload_date": datetime.now() - timedelta(days=1),
            "status": "AI Enhanced",
            "file_size": "1.8 MB", 
            "processing_time": "3.2s",
            "outputs": ["Enhanced Markdown", "RAG Vector Store", "Dashboard Entry"],
            "ai_summary": "High-end residential electrical installation with smart home integration, solar panel preparation, and premium fixtures. 45 units with standardized electrical packages.",
            "vector_store_id": "file_res456def",
            "location": "Portland, OR"
        },
        {
            "company_name": "Industrial Power Solutions",
            "project_name": "Manufacturing Warehouse B",
            "project_type": "Industrial",
            "upload_date": datetime.now() - timedelta(days=2),
            "status": "AI Enhanced", 
            "file_size": "945 KB",
            "processing_time": "2.1s",
            "outputs": ["Enhanced Markdown", "RAG Vector Store"],
            "ai_summary": "Industrial electrical infrastructure for manufacturing facility with heavy machinery power requirements, safety systems, and automated controls.",
            "vector_store_id": "file_ind789ghi",
            "location": "Denver, CO"
        }
    ]

if 'rag_knowledge_files' not in st.session_state:
    st.session_state.rag_knowledge_files = [
        {"name": "Commercial_Template_Enhanced.md", "type": "Enhanced Project", "usage": 45, "company": "ABC Electrical", "date": "2025-07-01"},
        {"name": "Residential_Format_AI.md", "type": "Enhanced Project", "usage": 23, "company": "Residential Plus", "date": "2025-06-30"},
        {"name": "Industrial_Examples_Enhanced.md", "type": "Enhanced Project", "usage": 12, "company": "Industrial Power", "date": "2025-06-29"},
        {"name": "Standard_Commercial_Template.docx", "type": "Manual Template", "usage": 8, "company": "System", "date": "2025-06-25"},
        {"name": "Few_Shot_Examples.pdf", "type": "Training Data", "usage": 15, "company": "System", "date": "2025-06-20"}
    ]

# Page Header
st.title("📊 Dashboard & Management")
st.caption("Monitor your AccuBid conversions and manage system settings")

# Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h2>47</h2>
        <p>AI Enhanced Projects</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h2>3.4s</h2>
        <p>Avg AI Processing Time</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h2>100%</h2>
        <p>RAG Upload Success</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <h2>47</h2>
        <p>Vector Store Entries</p>
    </div>
    """, unsafe_allow_html=True)

# Main Dashboard Content - Project History Only

st.markdown("""
<div class="dashboard-card">
    <h3>🏢 AI Enhanced Project History</h3>
    <p>View and manage your AccuBid projects that have been enhanced with AI analysis</p>
</div>
""", unsafe_allow_html=True)

# Search and filter
col_search, col_filter1, col_filter2 = st.columns([2, 1, 1])
with col_search:
    search_term = st.text_input("🔍 Search projects", placeholder="Search by company or project name...")
with col_filter1:
    company_filter = st.selectbox("Filter by company", ["All Companies"] + list(set([p["company_name"] for p in st.session_state.project_history])))
with col_filter2:
    type_filter = st.selectbox("Filter by type", ["All Types", "Commercial", "Residential", "Industrial", "Institutional"])

# Project history list
for project_data in st.session_state.project_history:
    # Apply filters
    if search_term and search_term.lower() not in project_data["company_name"].lower() and search_term.lower() not in project_data["project_name"].lower():
        continue
    if company_filter != "All Companies" and project_data["company_name"] != company_filter:
        continue
    if type_filter != "All Types" and project_data["project_type"] != type_filter:
        continue
        
    st.markdown(f"""
    <div class="file-item">
        <h4>🏢 {project_data["company_name"]} - {project_data["project_name"]}</h4>
        <p><strong>Type:</strong> {project_data["project_type"]} | <strong>Location:</strong> {project_data.get("location", "Not specified")}</p>
        <p><strong>Processed:</strong> {project_data["upload_date"].strftime("%Y-%m-%d %H:%M")}</p>
        <p><strong>Status:</strong> <span class="status-active">{project_data["status"]}</span></p>
        <p><strong>AI Processing Time:</strong> {project_data["processing_time"]} | <strong>File Size:</strong> {project_data["file_size"]}</p>
        <p><strong>Outputs:</strong> {", ".join(project_data["outputs"])}</p>
        <p><strong>AI Summary:</strong> <em>{project_data["ai_summary"][:150]}...</em></p>
        <p><strong>Vector Store ID:</strong> <code>{project_data["vector_store_id"]}</code></p>
    </div>
    """, unsafe_allow_html=True)
    
    col_chat, col_markdown, col_regenerate, col_delete = st.columns(4)
    with col_chat:
        if st.button(f"💬 Chat", key=f"chat_{project_data['project_name']}", help="Start a conversation about this project"):
            st.info("Navigate to Chat page to ask questions about this project!")
    with col_markdown:
        if st.button(f"📄 View Markdown", key=f"markdown_{project_data['project_name']}", help="View the AI-enhanced markdown file"):
            st.success("Markdown viewing will be implemented in backend phase")
    with col_regenerate:
        if st.button(f"🔄 Re-enhance", key=f"regenerate_{project_data['project_name']}", help="Re-run AI enhancement"):
            st.success("AI re-enhancement will be implemented in backend phase")
    with col_delete:
        if st.button(f"🗑️ Delete", key=f"delete_{project_data['project_name']}", help="Remove from system"):
            st.error("Delete functionality will be implemented in backend phase")
