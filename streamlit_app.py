import streamlit as st
import os
import time
from datetime import datetime
from groupme_internships import (
    get_internship_info, 
    topic_handler, 
    post_to_subgroup,
    CS_ID, ENGINEERING_ID, MED_ID, LAW_ID, BUSINESS_ID, HUMANITIES_ID
)

# Set page config
st.set_page_config(
    page_title="Ladders GroupMe Internship Bot Dashboard",
    page_icon="💼",
    layout="wide"
)

# Title and description
st.title("💼 Ladders GroupMe Internship Bot Dashboard")
st.markdown("**Control your internship bot with individual subgroup buttons or post to all at once!**")

# Check if environment variables are loaded
if not all([CS_ID, ENGINEERING_ID, MED_ID, LAW_ID, BUSINESS_ID, HUMANITIES_ID]):
    st.error("⚠️ Missing environment variables! Please check your .env file.")
    st.stop()

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'last_fetch' not in st.session_state:
    st.session_state.last_fetch = None

# Sidebar with bot status and controls
st.sidebar.header("🤖 Bot Status")

# Fetch data button
if st.sidebar.button("🔄 Fetch Latest Internships", type="primary"):
    with st.sidebar:
        with st.spinner("Fetching internships..."):
            st.session_state.data = get_internship_info()
            st.session_state.last_fetch = datetime.now()
            st.success("✅ Data fetched successfully!")

# Show last fetch time
if st.session_state.last_fetch:
    st.sidebar.info(f"📅 Last fetched: {st.session_state.last_fetch.strftime('%Y-%m-%d %H:%M:%S')}")

# Show data summary if available
if st.session_state.data and isinstance(st.session_state.data, dict):
    st.sidebar.header("📊 Data Summary")
    for category, jobs in st.session_state.data.items():
        if jobs:  # Only show categories with jobs
            st.sidebar.metric(category, len(jobs))

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎯 Post to Subgroups")
    
    # Check if data is available
    if st.session_state.data is None:
        st.warning("📥 Please fetch internship data first using the sidebar button.")
    elif isinstance(st.session_state.data, str):
        st.error(f"❌ Error fetching data: {st.session_state.data}")
    else:
        # Individual subgroup buttons
        st.subheader("Individual Subgroups")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🖥️ CS/IT Subgroup", use_container_width=True):
                if st.session_state.data.get("CS/IT"):
                    with st.spinner("Posting to CS/IT subgroup..."):
                        cs_messages = topic_handler("CS/IT", st.session_state.data)
                        for message in cs_messages:
                            post_to_subgroup(message, CS_ID)
                            time.sleep(1)
                    st.success(f"✅ Posted {len(cs_messages)} message(s) to CS/IT subgroup!")
                else:
                    st.info("ℹ️ No CS/IT internships available.")
            
            if st.button("🩺 Health Sciences Subgroup", use_container_width=True):
                if st.session_state.data.get("Health Sciences"):
                    with st.spinner("Posting to Health Sciences subgroup..."):
                        health_messages = topic_handler("Health Sciences", st.session_state.data)
                        for message in health_messages:
                            post_to_subgroup(message, MED_ID)
                            time.sleep(1)
                    st.success(f"✅ Posted {len(health_messages)} message(s) to Health Sciences subgroup!")
                else:
                    st.info("ℹ️ No Health Sciences internships available.")
        
        with col_b:
            if st.button("🛠️ Engineering Subgroup", use_container_width=True):
                if st.session_state.data.get("Engineering"):
                    with st.spinner("Posting to Engineering subgroup..."):
                        eng_messages = topic_handler("Engineering", st.session_state.data)
                        for message in eng_messages:
                            post_to_subgroup(message, ENGINEERING_ID)
                            time.sleep(1)
                    st.success(f"✅ Posted {len(eng_messages)} message(s) to Engineering subgroup!")
                else:
                    st.info("ℹ️ No Engineering internships available.")
            
            if st.button("⚖️ Social Sciences/Law Subgroup", use_container_width=True):
                if st.session_state.data.get("Social Sciences / Law"):
                    with st.spinner("Posting to Social Sciences/Law subgroup..."):
                        social_messages = topic_handler("Social Sciences/Law", st.session_state.data)
                        for message in social_messages:
                            post_to_subgroup(message, LAW_ID)
                            time.sleep(1)
                    st.success(f"✅ Posted {len(social_messages)} message(s) to Social Sciences/Law subgroup!")
                else:
                    st.info("ℹ️ No Social Sciences/Law internships available.")
        
        with col_c:
            if st.button("💼 Business Subgroup", use_container_width=True):
                if st.session_state.data.get("Business"):
                    with st.spinner("Posting to Business subgroup..."):
                        business_messages = topic_handler("Business", st.session_state.data)
                        for message in business_messages:
                            post_to_subgroup(message, BUSINESS_ID)
                            time.sleep(1)
                    st.success(f"✅ Posted {len(business_messages)} message(s) to Business subgroup!")
                else:
                    st.info("ℹ️ No Business internships available.")
            
            if st.button("🎨 Humanities Subgroup", use_container_width=True):
                if st.session_state.data.get("Humanities"):
                    with st.spinner("Posting to Humanities subgroup..."):
                        humanities_messages = topic_handler("Humanities", st.session_state.data)
                        for message in humanities_messages:
                            post_to_subgroup(message, HUMANITIES_ID)
                            time.sleep(1)
                    st.success(f"✅ Posted {len(humanities_messages)} message(s) to Humanities subgroup!")
                else:
                    st.info("ℹ️ No Humanities internships available.")
        
        # Post to all subgroups button
        st.markdown("---")
        st.subheader("🚀 Post to All Subgroups")
        
        if st.button("📢 POST TO ALL SUBGROUPS", type="primary", use_container_width=True):
            total_messages = 0
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            categories = [
                ("CS/IT", CS_ID, "🖥️"),
                ("Engineering", ENGINEERING_ID, "🛠️"), 
                ("Health Sciences", MED_ID, "🩺"),
                ("Social Sciences/Law", LAW_ID, "⚖️"),
                ("Business", BUSINESS_ID, "💼"),
                ("Humanities", HUMANITIES_ID, "🎨")
            ]
            
            for i, (category, subgroup_id, emoji) in enumerate(categories):
                status_text.text(f"Posting to {emoji} {category}...")
                
                if st.session_state.data.get(category.replace("/", " / ")):  # Handle category name format
                    messages = topic_handler(category, st.session_state.data)
                    for message in messages:
                        post_to_subgroup(message, subgroup_id)
                        time.sleep(1)
                    total_messages += len(messages)
                
                progress_bar.progress((i + 1) / len(categories))
                time.sleep(0.5)
            
            status_text.empty()
            progress_bar.empty()
            st.success(f"🎉 Successfully posted {total_messages} message(s) to all subgroups!")

with col2:
    st.header("📋 Preview Data")
    
    if st.session_state.data and isinstance(st.session_state.data, dict):
        # Show preview of each category
        for category, jobs in st.session_state.data.items():
            if jobs:  # Only show categories with jobs
                with st.expander(f"{category} ({len(jobs)} jobs)"):
                    for i, (company, title, url) in enumerate(jobs[:3], 1):  # Show first 3
                        st.write(f"**{i}. {company}**")
                        st.write(f"   Position: {title}")
                        st.write(f"   URL: {url}")
                        st.write("---")
                    
                    if len(jobs) > 3:
                        st.write(f"... and {len(jobs) - 3} more")

# Footer
st.markdown("---")
st.markdown("**🤖 Ladders GroupMe Internship Bot** - Automated internship posting to categorized subgroups")
st.markdown("*Made with ❤️ using Streamlit*")
