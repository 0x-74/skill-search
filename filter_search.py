import streamlit as st
import urllib.parse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
def show_filter_search_page():
    st.subheader("🎯 Job Search Builder")
    
    with st.container():
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input(
                "Job Title/Keywords",
                placeholder="e.g., Python Developer, Data Scientist",
                help="Enter job title or keywords to search for",
                key="job_title_filter"
            )
            
            exp_level = st.multiselect(
                "Experience Level",
                ["Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"],
                help="Select one or more experience levels",
                key="exp_level_filter"
            )
        
        with col2:
            job_type = st.multiselect(
                "Job Type",
                ["Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"],
                help="Select employment types",
                key="job_type_filter"
            )
            
            remote_options = st.selectbox(
                "Work Location",
                ["Any", "Remote", "On-site", "Hybrid"],
                help="Filter by work arrangement",
                key="remote_options_filter"
            )
            
            date_posted = st.selectbox(
                "Date Posted",
                ["Any time", "Past 24 hours", "Past week", "Past month"],
                help="Filter by how recently the job was posted",
                key="date_posted_filter"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Build URL from filters
    url = ""
    if job_title:
        base_url = "https://www.linkedin.com/jobs/search/?"
        params = {}
        
        if job_title:
            params['keywords'] = job_title
        if exp_level:
            exp_mapping = {
                "Internship": "1", "Entry level": "2", "Associate": "3",
                "Mid-Senior level": "4", "Director": "5", "Executive": "6"
            }
            params['f_E'] = ','.join([exp_mapping[level] for level in exp_level])
        if job_type:
            type_mapping = {
                "Full-time": "F", "Part-time": "P", "Contract": "C",
                "Temporary": "T", "Volunteer": "V", "Internship": "I", "Other": "O"
            }
            params['f_JT'] = ','.join([type_mapping[jtype] for jtype in job_type])
        if remote_options != "Any":
            remote_mapping = {"Remote": "2", "On-site": "1", "Hybrid": "3"}
            params['f_WT'] = remote_mapping[remote_options]
        if date_posted != "Any time":
            date_mapping = {
                "Past 24 hours": "r86400", "Past week": "r604800", "Past month": "r2592000"
            }
            params['f_TPR'] = date_mapping[date_posted]
        
        url = base_url + urllib.parse.urlencode(params)
        
        st.info(f"🔗 Generated URL: `{url}`")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        if url and url.strip():
            if st.button("🔍 Start Scraping Setup", type="primary", use_container_width=True):
                try:
                    if st.session_state.driver is None:
                        with st.spinner("Initializing browser..."):
                            service = webdriver.Chrome(service=ChromeDriverManager().install())
                            options = webdriver.ChromeOptions()
                            options.add_argument('--disable-gpu')
                            options.add_argument("--headless")
                            st.session_state.driver = webdriver.Chrome(options=options, service=service)
                    
                    with st.spinner("Loading LinkedIn page..."):
                        st.session_state.driver.get(url)
                    
                    st.session_state.current_url = url
                    st.session_state.show_url_dialog = True
                    st.success("✅ Page loaded successfully!")
                    st.rerun()
                    
                except Exception as e:
                    if st.session_state.driver:
                        st.session_state.driver.quit()
                        st.session_state.driver = None
                    st.error(f"❌ Error loading page: {e}")

    with col2:
        status_color = "status-active" if st.session_state.is_scraping else "status-inactive"
        status_text = "Scraping in progress..." if st.session_state.is_scraping else "Ready to scrape"
        
        st.markdown(f"""
        <div class="filter-section">
            <h4 style="color: #0077B5 !important;">📊 Scraping Status</h4>
            <p style="color: #333 !important;"><span class="status-indicator {status_color}"></span>{status_text}</p>
        </div>
        """, unsafe_allow_html=True)

    # Show dialogs
    if st.session_state.show_url_dialog:
        show_filter_confirmation_dialog()

def show_filter_confirmation_dialog():
    with st.container():
        st.markdown("---")
        st.subheader("✅ Confirm LinkedIn Page")
        st.write("Please verify that the LinkedIn page loaded correctly with your desired job listings.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Looks Good", type="primary", use_container_width=True, key="filter_looks_good"):
                st.session_state.correctUrl = True
                st.session_state.show_url_dialog = False
                st.session_state.scraping_started = True
                st.rerun()
        
        with col2:
            if st.button("❌ Not Right", type="secondary", use_container_width=True, key="filter_not_right"):
                st.session_state.correctUrl = False
                st.session_state.show_url_dialog = False
                if st.session_state.driver:
                    st.session_state.driver.quit()
                    st.session_state.driver = None
                st.rerun()
        
        with col3:
            if st.button("🔄 Reload Page", use_container_width=True, key="filter_reload"):
                try:
                    st.session_state.driver.refresh()
                    st.success("Page reloaded!")
                except Exception as e:
                    st.error(f"Error reloading: {e}")