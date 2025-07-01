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
if 'file_history' not in st.session_state:
    st.session_state.file_history = [
        {
            "filename": "Commercial_Plaza_Project.xlsx",
            "upload_date": datetime.now() - timedelta(hours=2),
            "status": "Completed",
            "file_size": "2.3 MB",
            "conversion_time": "3.2s",
            "outputs": ["Word Document", "PDF Report"]
        },
        {
            "filename": "Residential_Complex_A.xlsx", 
            "upload_date": datetime.now() - timedelta(days=1),
            "status": "Completed",
            "file_size": "1.8 MB", 
            "conversion_time": "2.1s",
            "outputs": ["Word Document", "PDF Report"]
        },
        {
            "filename": "Industrial_Warehouse_B.csv",
            "upload_date": datetime.now() - timedelta(days=2),
            "status": "Completed", 
            "file_size": "945 KB",
            "conversion_time": "1.8s",
            "outputs": ["Word Document"]
        }
    ]

if 'knowledge_base_files' not in st.session_state:
    st.session_state.knowledge_base_files = [
        {"name": "Standard_Commercial_Template.docx", "type": "Template", "usage": 45},
        {"name": "Residential_Format_Guide.pdf", "type": "Guide", "usage": 23},
        {"name": "Industrial_Examples.xlsx", "type": "Examples", "usage": 12}
    ]

# Page Header
st.title("📊 Dashboard & Management")
st.caption("Monitor your AccuBid conversions and manage system settings")

# Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h2>124</h2>
        <p>Total Conversions</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h2>2.3s</h2>
        <p>Avg Processing Time</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h2>98.5%</h2>
        <p>Success Rate</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <h2>12</h2>
        <p>Active Templates</p>
    </div>
    """, unsafe_allow_html=True)

# Main Dashboard Content
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 File History", "🧠 Knowledge Base", "🔗 Integrations", "📝 Templates", "📈 Analytics"])

with tab1:
    st.markdown("""
    <div class="dashboard-card">
        <h3>📁 File Processing History</h3>
        <p>View and manage your processed AccuBid files</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search and filter
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_term = st.text_input("🔍 Search files", placeholder="Search by filename...")
    with col_filter:
        status_filter = st.selectbox("Filter by status", ["All", "Completed", "Processing", "Error"])
    
    # File history list
    for file_data in st.session_state.file_history:
        if search_term and search_term.lower() not in file_data["filename"].lower():
            continue
            
        st.markdown(f"""
        <div class="file-item">
            <h4>📄 {file_data["filename"]}</h4>
            <p><strong>Uploaded:</strong> {file_data["upload_date"].strftime("%Y-%m-%d %H:%M")}</p>
            <p><strong>Status:</strong> <span class="status-active">{file_data["status"]}</span></p>
            <p><strong>Size:</strong> {file_data["file_size"]} | <strong>Processing Time:</strong> {file_data["conversion_time"]}</p>
            <p><strong>Outputs:</strong> {", ".join(file_data["outputs"])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_download, col_reprocess, col_delete = st.columns(3)
        with col_download:
            if st.button(f"⬇️ Download", key=f"download_{file_data['filename']}"):
                st.success("Download functionality will be implemented in backend phase")
        with col_reprocess:
            if st.button(f"🔄 Reprocess", key=f"reprocess_{file_data['filename']}"):
                st.success("Reprocessing functionality will be implemented in backend phase")
        with col_delete:
            if st.button(f"🗑️ Delete", key=f"delete_{file_data['filename']}"):
                st.error("Delete functionality will be implemented in backend phase")

with tab2:
    st.markdown("""
    <div class="dashboard-card">
        <h3>🧠 RAG Knowledge Base</h3>
        <p>Manage templates, examples, and training data for improved AI responses</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload new knowledge base files
    st.subheader("📤 Add to Knowledge Base")
    
    col_upload, col_type = st.columns([2, 1])
    with col_upload:
        kb_file = st.file_uploader(
            "Upload templates, examples, or guides",
            type=['docx', 'pdf', 'xlsx', 'txt'],
            help="These files will help AI generate better formatted documents"
        )
    with col_type:
        file_type = st.selectbox("File Type", ["Template", "Example", "Guide", "Standard"])
    
    if kb_file and st.button("📚 Add to Knowledge Base"):
        st.success(f"Added {kb_file.name} to knowledge base as {file_type}")
        st.session_state.knowledge_base_files.append({
            "name": kb_file.name,
            "type": file_type,
            "usage": 0
        })
        st.rerun()
    
    # Current knowledge base
    st.subheader("📚 Current Knowledge Base")
    
    for kb_file in st.session_state.knowledge_base_files:
        st.markdown(f"""
        <div class="template-item">
            <h4>📄 {kb_file["name"]}</h4>
            <p><strong>Type:</strong> {kb_file["type"]} | <strong>Usage Count:</strong> {kb_file["usage"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_edit, col_remove = st.columns(2)
        with col_edit:
            if st.button(f"✏️ Edit", key=f"edit_kb_{kb_file['name']}"):
                st.info("Edit functionality will be implemented in backend phase")
        with col_remove:
            if st.button(f"🗑️ Remove", key=f"remove_kb_{kb_file['name']}"):
                st.warning("Remove functionality will be implemented in backend phase")
    
    # RAG Update Schedule
    st.subheader("⏰ Automatic Updates")
    st.markdown("""
    <div class="integration-card">
        <h4>🔄 Scheduled RAG Updates</h4>
        <p><strong>Status:</strong> <span class="status-active">Active</span></p>
        <p><strong>Frequency:</strong> Every hour</p>
        <p><strong>Last Update:</strong> 23 minutes ago</p>
        <p><strong>Next Update:</strong> In 37 minutes</p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class="dashboard-card">
        <h3>🔗 External Integrations</h3>
        <p>Configure connections to email, calendar, and Excel services</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Email Integration
    st.subheader("📧 Email Configuration")
    with st.expander("Email Settings", expanded=False):
        email_provider = st.selectbox("Email Provider", ["Gmail", "Outlook", "Custom SMTP"])
        email_address = st.text_input("Email Address", placeholder="your-email@domain.com")
        if email_provider == "Custom SMTP":
            smtp_server = st.text_input("SMTP Server", placeholder="smtp.yourprovider.com")
            smtp_port = st.number_input("SMTP Port", value=587)
        
        if st.button("🔧 Test Email Connection"):
            st.success("Email integration will be implemented in backend phase")
    
    # Calendar Integration
    st.subheader("📅 Calendar Integration")
    with st.expander("Calendar Settings", expanded=False):
        calendar_provider = st.selectbox("Calendar Provider", ["Google Calendar", "Outlook Calendar", "Apple Calendar"])
        calendar_timezone = st.selectbox("Timezone", ["UTC-8 (PST)", "UTC-5 (EST)", "UTC+0 (GMT)"])
        
        if st.button("🔧 Test Calendar Connection"):
            st.success("Calendar integration will be implemented in backend phase")
    
    # Excel API
    st.subheader("📊 Excel API Integration")  
    with st.expander("Excel Settings", expanded=False):
        excel_service = st.selectbox("Excel Service", ["Microsoft Graph API", "Google Sheets API", "Local Excel"])
        
        if excel_service != "Local Excel":
            api_key = st.text_input("API Key", type="password", placeholder="Enter your API key")
        
        if st.button("🔧 Test Excel Connection"):
            st.success("Excel integration will be implemented in backend phase")
    
    # Integration Status
    st.subheader("🔍 Integration Status")
    
    integrations = [
        {"name": "Email (SMTP)", "status": "Connected", "last_used": "2 hours ago"},
        {"name": "Google Calendar", "status": "Disconnected", "last_used": "Never"},
        {"name": "Excel API", "status": "Error", "last_used": "1 day ago"},
        {"name": "Supabase Database", "status": "Connected", "last_used": "Active"}
    ]
    
    for integration in integrations:
        status_class = "status-active" if integration["status"] == "Connected" else "status-error" if integration["status"] == "Error" else "status-inactive"
        
        st.markdown(f"""
        <div class="integration-card">
            <h4>{integration["name"]}</h4>
            <p><strong>Status:</strong> <span class="{status_class}">{integration["status"]}</span></p>
            <p><strong>Last Used:</strong> {integration["last_used"]}</p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <div class="dashboard-card">
        <h3>📝 Document Templates & Few-Shot Examples</h3>
        <p>Manage AI prompting templates and document formatting examples</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create new template
    st.subheader("➕ Create New Template")
    
    col_name, col_type = st.columns(2)
    with col_name:
        template_name = st.text_input("Template Name", placeholder="e.g., Commercial Project Format")
    with col_type:
        template_type = st.selectbox("Template Type", ["Few-Shot Example", "Document Format", "Prompt Template"])
    
    template_content = st.text_area(
        "Template Content",
        height=200,
        placeholder="Enter your template content, few-shot examples, or prompting instructions..."
    )
    
    if template_name and template_content:
        if st.button("💾 Save Template"):
            st.success(f"Template '{template_name}' saved successfully!")
    
    # Existing templates
    st.subheader("📄 Existing Templates")
    
    mock_templates = [
        {
            "name": "Commercial Standard Format",
            "type": "Few-Shot Example", 
            "usage": 89,
            "effectiveness": "94%"
        },
        {
            "name": "Residential Simple Layout",
            "type": "Document Format",
            "usage": 67,
            "effectiveness": "91%"
        },
        {
            "name": "Cost Breakdown Prompt",
            "type": "Prompt Template",
            "usage": 134,
            "effectiveness": "96%"
        }
    ]
    
    for template in mock_templates:
        st.markdown(f"""
        <div class="template-item">
            <h4>📄 {template["name"]}</h4>
            <p><strong>Type:</strong> {template["type"]}</p>
            <p><strong>Usage:</strong> {template["usage"]} times | <strong>Effectiveness:</strong> {template["effectiveness"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_edit, col_test, col_delete = st.columns(3)
        with col_edit:
            if st.button(f"✏️ Edit", key=f"edit_template_{template['name']}"):
                st.info("Template editing will be implemented in backend phase")
        with col_test:
            if st.button(f"🧪 Test", key=f"test_template_{template['name']}"):
                st.info("Template testing will be implemented in backend phase")
        with col_delete:
            if st.button(f"🗑️ Delete", key=f"delete_template_{template['name']}"):
                st.warning("Template deletion will be implemented in backend phase")

with tab5:
    st.markdown("""
    <div class="dashboard-card">
        <h3>📈 Usage Analytics</h3>
        <p>Monitor system performance and user behavior</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Time range selector
    time_range = st.selectbox("📅 Time Range", ["Last 7 days", "Last 30 days", "Last 3 months", "All time"])
    
    # Mock analytics data
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 Conversion Volume")
        # Mock data for chart
        dates = pd.date_range(start='2025-06-22', end='2025-06-28', freq='D')
        conversions = [8, 12, 15, 10, 18, 14, 22]
        
        chart_data = pd.DataFrame({
            'Date': dates,
            'Conversions': conversions
        })
        
        st.line_chart(chart_data.set_index('Date'))
    
    with col_chart2:
        st.subheader("⚡ Processing Times")
        # Mock processing time data
        times_data = pd.DataFrame({
            'File Size Range': ['< 1MB', '1-5MB', '5-10MB', '> 10MB'],
            'Avg Time (seconds)': [1.2, 2.3, 4.1, 7.8]
        })
        
        st.bar_chart(times_data.set_index('File Size Range'))
    
    # Key metrics
    st.subheader("🎯 Key Performance Indicators")
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    with col_kpi1:
        st.metric("Success Rate", "98.5%", "+2.1%")
        
    with col_kpi2:
        st.metric("Avg Processing Time", "2.3s", "-0.4s")
        
    with col_kpi3:
        st.metric("User Satisfaction", "4.8/5", "+0.2")
    
    # Error analysis
    st.subheader("🔍 Error Analysis")
    
    error_data = {
        "Error Type": ["File Format Issues", "Processing Timeout", "AI Generation Error", "Export Failure"],
        "Count": [3, 1, 2, 1],
        "Percentage": ["42.9%", "14.3%", "28.6%", "14.3%"]
    }
    
    error_df = pd.DataFrame(error_data)
    st.table(error_df)
    
    # Usage patterns
    st.subheader("📊 Usage Patterns")
    
    col_pattern1, col_pattern2 = st.columns(2)
    
    with col_pattern1:
        st.markdown("**Most Popular Features:**")
        features = ["Word Document Export", "PDF Generation", "Email Integration", "Chat Assistant", "Template Usage"]
        usage_counts = [89, 76, 45, 34, 23]
        
        for feature, count in zip(features, usage_counts):
            st.write(f"• {feature}: {count} uses")
    
    with col_pattern2:
        st.markdown("**Peak Usage Times:**")
        st.write("• 9:00 AM - 11:00 AM: 35% of daily usage")
        st.write("• 2:00 PM - 4:00 PM: 28% of daily usage") 
        st.write("• 7:00 PM - 9:00 PM: 22% of daily usage")
        st.write("• Other hours: 15% of daily usage")
