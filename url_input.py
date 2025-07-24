import streamlit as st
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
JOB_SEARCH_RE = re.compile(
    r"^https:\/\/(?:www\.)?linkedin\.com\/jobs\/search\/?(?:\?.*)?$"
)

def show_url_input_page():
    st.subheader("🔗 Direct URL Input")
    
    url = st.text_input(
        "Enter LinkedIn Jobs Search URL",
        placeholder="https://www.linkedin.com/jobs/search/?keywords=python&location=...",
        key="direct_url_input"
    )
    
    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        if url and url.strip():
            if JOB_SEARCH_RE.match(url):
                if st.button("🔍 Start Scraping Setup", type="primary", use_container_width=True):
                    try:
                        if st.session_state.driver is None:
                            with st.spinner("Initializing browser..."):
                                options = Options()
                                options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
                                options.add_argument("--disable-blink-features=AutomationControlled")
                                options.add_argument('--disable-gpu')
                                options.add_argument("--headless")
                                # options.add_argument("start-maximized")
                                options.add_argument("disable-infobars")
                                options.add_argument("--disable-extensions")
                                options.add_argument('--no-sandbox')
                                options.add_argument('--disable-application-cache')
                                options.add_argument('--disable-gpu')
                                options.add_argument("--disable-dev-shm-usage")
                                st.session_state.driver = webdriver.Firefox(options=options, )
                        
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
            else:
                st.warning("⚠️ Please enter a valid LinkedIn jobs search URL")

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
        show_url_confirmation_dialog()

def show_url_confirmation_dialog():
    with st.container():
        st.markdown("---")
        st.subheader("✅ Confirm LinkedIn Page")
        st.write("Please verify that the LinkedIn page loaded correctly with your desired job listings.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Looks Good", type="primary", use_container_width=True):
                st.session_state.correctUrl = True
                st.session_state.show_url_dialog = False
                st.session_state.scraping_started = True
                st.rerun()
        
        with col2:
            if st.button("❌ Not Right", type="secondary", use_container_width=True):
                st.session_state.correctUrl = False
                st.session_state.show_url_dialog = False
                if st.session_state.driver:
                    st.session_state.driver.quit()
                    st.session_state.driver = None
                st.rerun()
        
        with col3:
            if st.button("🔄 Reload Page", use_container_width=True):
                try:
                    st.session_state.driver.refresh()
                    st.success("Page reloaded!")
                except Exception as e:
                    st.error(f"Error reloading: {e}")