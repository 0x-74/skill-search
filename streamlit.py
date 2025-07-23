import os
from analytics import show_visualization_page
import streamlit as st
from url_input import show_url_input_page
from filter_search import show_filter_search_page
from scraper import run_scraper
from job_parser import show_job_parser_page

@st.cache_data
def installff():
    os.system('sbase install geckodriver')
    os.system('ln -s /home/adminuser/venv/lib/python3.11/site-packages/seleniumbase/drivers/geckodriver /home/adminuser/venv/bin/geckodriver')

_ = installff()
# Initialize session state
def initialize_session_state():
    for key, default in {
        "driver": None,
        "show_url_dialog": False,
        "correctUrl": None,
        "filename": None,
        "show_filename_dialog": False,
        "show_email_pass_dialog": False,
        "mail": None,
        "password": None,
        "cookie": None,
        "scraping_progress": [],
        "is_scraping": False,
        "total_jobs_scraped": 0,
        "first_job_displayed": False,
        "scraping_started": False,
        "current_url": None,
        "input_method": "Direct LinkedIn URL",
        "parsing_in_progress": False,
        "parsing_state": None,
        "llm_configured": False,
        "current_model": None,
        "selected_file_path": None,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

# Page configuration
st.set_page_config(
    page_title="LinkedIn Job Scraper",
    page_icon="💼",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0077B5, #00A0DC);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .filter-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
        color: #333;
    }
    .progress-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
        color: #333;
        max-height: 400px;
        overflow-y: auto;
    }
    .job-count {
        font-size: 1.2rem;
        font-weight: bold;
        color: #0077B5;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-active { background-color: #28a745; }
    .status-inactive { background-color: #6c757d; }
    
    .filter-section h4 {
        color: #0077B5 !important;
        margin-bottom: 0.5rem;
    }
    .filter-section p {
        color: #333 !important;
        margin-bottom: 0.25rem;
    }
    
    .stMarkdown {
        color: #333;
    }
    
    /* Hide radio buttons when scraping */
    .scraping-disabled {
        pointer-events: none;
        opacity: 0.5;
    }
    
    /* Fixed height for log container */
    .log-container {
        height: 300px;
        overflow-y: auto;
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💼 LinkedIn Job Scraper</h1>
        <p>Extract job listings with advanced filters and real-time monitoring</p>
    </div>
    """, unsafe_allow_html=True)

    # Show different content based on scraping state
    if st.session_state.scraping_started:
        # Show scraper interface when scraping has started
        run_scraper()
    else:
        # Navigation tabs for different functions
        tab1, tab2, tab3 = st.tabs(["🔍 Job Search", "🧠 AI Parser", "📊 Analytics"])
        
        with tab1:
            # Show input method selection only when not scraping
            with st.sidebar:
                st.header("🔍 Search Method")
                
                input_method = st.radio(
                    "Choose Search Method",
                    ["Direct LinkedIn URL", "Job Search with Filters"],
                    index=0 if st.session_state.input_method == "Direct LinkedIn URL" else 1,
                    help="Choose how you want to search for jobs"
                )
                st.session_state.input_method = input_method

            # Show appropriate input page based on selection
            if input_method == "Direct LinkedIn URL":
                show_url_input_page()
            else:
                show_filter_search_page()
        
        with tab2:
            # Job parsing and analysis page
            show_job_parser_page()
        
        with tab3:
            # Placeholder for future analytics features
            show_visualization_page()

if __name__ == "__main__":
    main()