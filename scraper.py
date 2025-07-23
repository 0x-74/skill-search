import streamlit as st
import os
import time
from login import login
from main import click_next_page, get_job_cards, get_job_descriptions

def run_scraper():
    st.subheader("🤖 LinkedIn Job Scraper - Active Session")
    
    # Show current search method and URL (read-only)
    with st.expander("📋 Current Search Configuration", expanded=False):
        st.write(f"**Search Method:** {st.session_state.input_method}")
        st.write(f"**Target URL:** `{st.session_state.current_url}`")
        st.info("Configuration is locked during scraping session")

    if st.session_state.correctUrl is True:
        if not st.session_state.filename:
            st.session_state.show_filename_dialog = True

        if st.session_state.show_filename_dialog:
            show_filename_dialog()
        
        if st.session_state.filename:
            st.success(f"💾 Will save data to `{st.session_state.filename}.txt`")
            
            # Get credentials
            st.session_state.mail = st.session_state.mail or os.getenv('EMAIL')
            st.session_state.password = st.session_state.password or os.getenv('PASSWORD')
            st.session_state.cookie = st.session_state.cookie or os.getenv('COOKIE')
            
            if not st.session_state.mail or not st.session_state.password:
                st.session_state.show_email_pass_dialog = True

            if st.session_state.show_email_pass_dialog:
                show_credentials_dialog()
            else:
                show_scraping_interface()

def show_filename_dialog():
    st.markdown("---")
    st.subheader("📁 Save Configuration")
    st.write("Configure filename for saving the scraped job data:")
    
    file = st.text_input(
        "Filename (without extension)",
        placeholder="linkedin_jobs_2025",
        help="The data will be saved as a .txt file",
        key="filename_input"
    )
    
    if st.button("💾 Confirm Settings", type="primary", use_container_width=True):
        if file:
            st.session_state.filename = file
            st.session_state.show_filename_dialog = False
            st.rerun()
        else:
            st.error("Please enter a filename")

def show_credentials_dialog():
    st.markdown("---")
    st.subheader("🔐 LinkedIn Credentials")
    st.write("Enter your LinkedIn email and password. Optionally, add a `li_at` cookie to skip security challenges:")

    st.session_state.mail = st.text_input(
        "📧 Email",
        value=st.session_state.mail or "",
        placeholder="your-email@example.com",
        key="email_input"
    )

    st.session_state.password = st.text_input(
        "🔒 Password",
        type="password",
        value=st.session_state.password or "",
        placeholder="Your LinkedIn password",
        key="password_input"
    )

    st.session_state.cookie = st.text_area(
        "🍪 Optional `li_at` Cookie",
        value=st.session_state.cookie or "",
        placeholder="Paste your li_at cookie here (optional)...",
        key="cookie_input",
        height=70
    )

    st.info(
        "💡 *Tip:* Adding a `li_at` cookie skips OTP/security challenges. "
        "You can find it under Chrome → DevTools → Application → Cookies → `www.linkedin.com` → `li_at`."
    )

    if st.button("🚀 Start Scraping", type="primary", use_container_width=True):
        if st.session_state.mail and st.session_state.password:
            st.session_state.show_email_pass_dialog = False
            st.rerun()
        else:
            st.error("Please provide both email and password.")



def show_scraping_interface():
    # Live scraping section
    st.markdown("---")
    st.subheader("🔄 Live Scraping Progress")
    
    # Progress containers with fixed layout
    col1, col2 = st.columns(2)
    
    with col1:
        jobs_scraped_placeholder = st.empty()
    with col2:
        current_page_placeholder = st.empty()
    
    progress_bar = st.progress(0)
    
    # Fixed height log container to prevent infinite scrolling
    st.markdown("### 📝 Live Activity Log")
    log_placeholder = st.empty()
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not st.session_state.is_scraping:
            if st.button("🚀 Start Scraping Now!", type="primary", use_container_width=True):
                st.session_state.is_scraping = True
                st.session_state.scraping_progress = ["🔄 Initializing scraper..."]
                st.session_state.total_jobs_scraped = 0
                st.session_state.first_job_displayed = False
                st.rerun()
        else:
            st.button("⏸️ Scraping in Progress...", disabled=True, use_container_width=True)
    
    with col2:
        if st.button("🏠 New Search", use_container_width=True, disabled=st.session_state.is_scraping):
            reset_session()
            st.rerun()
    
    with col3:
        if st.button("🛑 Stop & Exit", use_container_width=True, type="secondary"):
            cleanup_and_exit()
            st.rerun()
    
    # Update display with current progress (fixed height container)
    with log_placeholder.container():
        if st.session_state.scraping_progress:
            # Create a fixed-height scrollable container
            log_text = "\n".join(st.session_state.scraping_progress[-20:])  # Show last 20 entries
            st.text_area(
                "Activity Log",
                value=log_text,
                height=300,
                disabled=True,
                key="activity_log"
            )
    
    # Update metrics
    jobs_scraped_placeholder.metric("Jobs Scraped", st.session_state.total_jobs_scraped)
    
    if st.session_state.is_scraping:
        execute_scraping_process(jobs_scraped_placeholder, current_page_placeholder, progress_bar, log_placeholder)

def execute_scraping_process(jobs_placeholder, page_placeholder, progress_bar, log_placeholder):
    try:
        # Login
        st.session_state.scraping_progress.append("🔐 Logging into LinkedIn...")
        update_log_display(log_placeholder)
        if st.session_state.cookie:
            st.session_state.scraping_progress.append("🔐 Logging in with cookie...")
            login(st.session_state.driver, st.session_state.mail, st.session_state.password, st.session_state.cookie)
            st.session_state.scraping_progress.append("✅ Logged in using cookie.")
        else:
            st.session_state.scraping_progress.append("🔐 Logging in with email/password...")
            login(st.session_state.driver, st.session_state.mail, st.session_state.password)
            st.session_state.scraping_progress.append("✅ Logged in successfully.")

        
        # Navigate to search results
        st.session_state.driver.get(st.session_state.current_url)
        st.session_state.scraping_progress.append(f"🔍 Navigating to search results")
        update_log_display(log_placeholder)
        
        all_descriptions = []
        page_number = 1
        on_last_page = False
        
        while not on_last_page and st.session_state.is_scraping:
            # Update status
            page_placeholder.metric("Current Page", page_number)
            
            # Get job cards and descriptions
            st.session_state.scraping_progress.append(f"📄 Processing page {page_number}...")
            update_log_display(log_placeholder)
            
            job_cards = get_job_cards(st.session_state.driver)
            job_descriptions = get_job_descriptions(job_cards, st.session_state.driver)
            
            # Display first job details when found
            if job_descriptions and not st.session_state.first_job_displayed:
                first_job = job_descriptions[0]
                lines = first_job.split('\n')
                job_title = lines[0] if lines else "Job title not found"
                
                st.session_state.scraping_progress.append(f"📋 First Job Found: {job_title}")
                st.session_state.scraping_progress.append(f"   Preview: {first_job[:100]}...")
                st.session_state.first_job_displayed = True
                update_log_display(log_placeholder)
            
            all_descriptions.extend(job_descriptions)
            st.session_state.total_jobs_scraped += len(job_descriptions)
            
            # Update metrics
            jobs_placeholder.metric("Jobs Scraped", st.session_state.total_jobs_scraped)
            
            st.session_state.scraping_progress.append(f"✅ Found {len(job_descriptions)} jobs on page {page_number}")
            update_log_display(log_placeholder)
            
            # Try to go to next page
            on_last_page = click_next_page(st.session_state.driver)
            
            if not on_last_page:
                page_number += 1
                progress_bar.progress(min(page_number / 25, 0.95))  # Estimate progress
                time.sleep(3)  # Rate limiting
            else:
                progress_bar.progress(1.0)
        
        # Save results
        st.session_state.scraping_progress.append(f"💾 Saving {len(all_descriptions)} job descriptions...")
        update_log_display(log_placeholder)
        
        filename = f'{st.session_state.filename}.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            for i, desc in enumerate(all_descriptions, 1):
                f.write(f"JOB #{i}\n")
                f.write("="*50 + "\n")
                f.write(desc + '\n\n')
                f.write('-'*80 + '\n\n')
        
        # Final status
        st.session_state.scraping_progress.append(f"✅ Successfully saved {len(all_descriptions)} jobs to {filename}")
        update_log_display(log_placeholder)
        
        st.success(f"🎉 Scraping completed! Saved {len(all_descriptions)} job descriptions to `{filename}`")
        
        # Download button
        with open(filename, 'r', encoding='utf-8') as f:
            st.download_button(
                label="📥 Download Results",
                data=f.read(),
                file_name=filename,
                mime="text/plain",
                type="primary"
            )
        
    except Exception as e:
        st.error(f"❌ Scraping failed: {e}")
        st.session_state.scraping_progress.append(f"❌ Error: {e}")
        update_log_display(log_placeholder)
    
    finally:
        st.session_state.is_scraping = False

def update_log_display(log_placeholder):
    """Update the log display with current progress"""
    with log_placeholder.container():
        if st.session_state.scraping_progress:
            # Show last 20 entries to prevent infinite scrolling
            log_text = "\n".join(st.session_state.scraping_progress[-20:])
            st.text_area(
                "Activity Log",
                value=log_text,
                height=300,
                disabled=True,
                key=f"activity_log_{len(st.session_state.scraping_progress)}"
            )

def reset_session():
    """Reset session to start a new search"""
    if st.session_state.driver:
        st.session_state.driver.quit()
    
    # Reset all relevant session state
    for key in ["driver", "show_url_dialog", "correctUrl", "filename", "show_filename_dialog", 
                "show_email_pass_dialog", "scraping_progress", "is_scraping", "total_jobs_scraped", 
                "first_job_displayed", "scraping_started", "current_url"]:
        if key in st.session_state:
            if key == "scraping_progress":
                st.session_state[key] = []
            elif key in ["is_scraping", "first_job_displayed", "scraping_started", "show_url_dialog", 
                        "show_filename_dialog", "show_email_pass_dialog"]:
                st.session_state[key] = False
            elif key in ["total_jobs_scraped"]:
                st.session_state[key] = 0
            else:
                st.session_state[key] = None

def cleanup_and_exit():
    """Clean up and exit the application"""
    if st.session_state.driver:
        st.session_state.driver.quit()
        st.session_state.driver = None
    st.session_state.is_scraping = False
    st.stop()