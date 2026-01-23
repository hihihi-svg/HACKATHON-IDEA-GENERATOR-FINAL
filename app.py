import streamlit as st
import re
import requests
from openai import OpenAI
from utils.summarizer import summarize_text
from utils.retriever import create_vector_db, retrieve_relevant_topics
from utils.resource_finder import find_relevant_resources
from utils.topic_generator import generate_hackathon_ideas
import utils.auth as auth

# ✅ Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Constants
USAGE_LIMIT = 2

st.set_page_config(page_title="Hackathon Idea Generator", page_icon="🚀", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main-header { font-size: 3rem; font-weight: bold; text-align: center; color: #1f77b4; margin-bottom: 1rem; }
    .sub-header { text-align: center; color: #666; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- Authentication Logic ---
if "user" not in st.session_state:
    st.session_state["user"] = None

def show_login_page():
    st.title("🔐 Login / Register")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user, msg = auth.login_user(username, password)
                if user:
                    st.session_state["user"] = user
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    
    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")
            new_email = st.text_input("Email (Optional)")
            submit_reg = st.form_submit_button("Register")
            
            if submit_reg:
                if len(new_user) < 3 or len(new_pass) < 3:
                    st.warning("Username and Password must be at least 3 characters.")
                else:
                    success, msg = auth.register_user(new_user, new_pass, new_email)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

# --- Main App Logic ---
if st.session_state["user"] is None:
    show_login_page()
else:
    # User is logged in
    user = st.session_state["user"]
    username = user["username"]
    
    # Refresh credits from DB to ensure accuracy
    current_credits = auth.get_credits(username)
    is_admin = user["is_admin"]

    # --- Header & Credits ---
    col_header, col_credits = st.columns([3, 1])
    
    with col_header:
        st.title("🚀 Hackathon Idea Generator")
        st.caption(f"Welcome, {username}!")
    
    with col_credits:
        col_logout, col_metric = st.columns([1, 2])
        with col_logout:
            if st.button("Logout"):
                st.session_state["user"] = None
                st.rerun()
        with col_metric:
            if not is_admin:
                st.metric("Credits Left", f"{current_credits}/{USAGE_LIMIT}", 
                         delta="Trial" if current_credits > 0 else "Empty",
                         delta_color="normal" if current_credits > 0 else "off")

    st.markdown("Generate innovative project ideas using your hackathon description and uploaded topics!")
    
    # --- Sidebar ---
    st.sidebar.header("📄 Upload Your Topics File (.docx)")
    st.sidebar.markdown("Upload a DOCX file containing relevant topics, technologies, or domain knowledge.")
    
    uploaded_file = st.sidebar.file_uploader("Upload DOCX", type=["docx"])
    
    if uploaded_file:
        import os
        import shutil
        os.makedirs("data", exist_ok=True)
        
        with open("data/topics.docx", "wb") as f:
            f.write(uploaded_file.read())
        st.sidebar.success("✅ Topics file uploaded!")
        
        # Helper for Window file locking
        def clear_vector_db(path):
            if os.path.exists(path):
                import gc
                import time
                try:
                    shutil.rmtree(path)
                except PermissionError:
                    gc.collect()
                    time.sleep(1)
                    try:
                        shutil.rmtree(path)
                    except Exception as e:
                        st.error(f"⚠️ Could not delete old DB (File in use). Please restart app locally. Error: {e}")
                except Exception as e:
                    st.error(f"❌ Error clearing database: {e}")

        if st.sidebar.button("🗑️ Clear Old Vector DB"):
            vector_db_path = "vectorstore/chroma_db"
            if os.path.exists(vector_db_path):
                clear_vector_db(vector_db_path)
                if not os.path.exists(vector_db_path):
                    st.sidebar.success("✅ Old vector database cleared!")
            else:
                st.sidebar.info("ℹ️ No existing database found")
    
        if st.sidebar.button("🔄 Create Vector DB"):
            with st.spinner("Creating vector database..."):
                vector_db_path = "vectorstore/chroma_db"
                clear_vector_db(vector_db_path)
                # Only create if cleared or didn't exist
                create_vector_db("data/topics.docx")
                st.sidebar.success("✅ Vector DB created successfully!")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ How It Works")
    st.sidebar.markdown("""
    1. **Upload Topics** (Optional)
    2. **Enter Description**
    3. **Generate Ideas**
    4. **Generate Content**
    """)
    
    st.sidebar.info("🌐 **Note:** This is a shared knowledge base! If you update the topics, it updates for everyone.")
    
    # --- Main Input Area ---
    st.markdown("## 📝 Hackathon Description")
    hackathon_text = st.text_area(
        "✍️ Paste your Hackathon / Competition Description", 
        height=150,
        placeholder="Example: Build an AI-powered healthcare solution..."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        summarize_btn = st.button("🧠 Summarize Theme", use_container_width=True)
    with col2:
        generate_btn = st.button("✨ Generate Ideas", use_container_width=True, type="primary")
    
    # Summarize Logic (No Credit Cost)
    if summarize_btn:
        if not hackathon_text:
            st.warning("⚠️ Please enter a hackathon description first.")
        else:
            with st.spinner("Analyzing theme..."):
                summary = summarize_text(hackathon_text)
                st.session_state["summary"] = summary
                st.markdown("### 🧠 Summarized Theme")
                st.info(summary)
    
    # Generation Logic (Costs Credits)
    if generate_btn:
        if not hackathon_text:
            st.warning("⚠️ Please enter a hackathon description first.")
        # Check Credits
        elif current_credits <= 0 and not is_admin:
            st.error("🚫 You have run out of credits! Ask the admin for more or create a new account.")
        else:
            with st.spinner("🔍 Analyzing and generating innovative ideas..."):
                # Deduct Credit if not admin
                if not is_admin:
                    auth.decrement_credits(username)
                    st.toast(f"Trial used! {current_credits - 1} remaining.", icon="ℹ️")
                
                # --- Generation Process ---
                summary = summarize_text(hackathon_text)
                st.session_state["summary"] = summary
                retrieved_topics = retrieve_relevant_topics(summary)
                resources = find_relevant_resources(summary)
                ideas = generate_hackathon_ideas(summary, retrieved_topics, resources)
                st.session_state["raw_ideas"] = ideas
                
                st.markdown("---")
                st.markdown("## 💡 Generated Hackathon Ideas")
                st.markdown(ideas)
                
                # Parse ideas for content generation
                lines = ideas.split('\n')
                parsed_ideas = []
                for line in lines:
                    if '|' in line and not line.strip().startswith('|---'):
                        cells = [c.strip() for c in line.split('|') if c.strip()]
                        if cells and cells[0].lower() not in ['title', 'summary', 'tech stack', 'example repo', 'novelty']:
                             # Simple 3-column check
                            if len(cells) >= 2:
                                parsed_ideas.append({
                                    'title': cells[0],
                                    'summary': cells[1] if len(cells) > 1 else '',
                                    'tech_stack': cells[2] if len(cells) > 2 else '',
                                })
                
                # Fallback parsing
                if not parsed_ideas:
                    title_pattern = r'(?:\d+\.\s*\*\*|###?\s*)([^:\n]+)'
                    titles = re.findall(title_pattern, ideas)
                    for title in titles[:5]:
                        parsed_ideas.append({'title': title.strip('*').strip(), 'summary': '', 'tech_stack': ''})
                
                st.session_state["parsed_ideas"] = parsed_ideas[:5]

    # --- Content Generation & Footer ---
    def extract_keywords_from_text(text):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "Extract 3-5 keywords, comma-separated."},
                          {"role": "user", "content": f"Extract from: {text}"}],
                temperature=0.3, max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except:
            return text[:50]

    if "parsed_ideas" in st.session_state and st.session_state["parsed_ideas"]:
        ideas_list = st.session_state["parsed_ideas"]
        st.markdown("---")
        st.markdown("## 📋 Generate Required Contents")
        
        for i, idea in enumerate(ideas_list):
            with st.expander(f"💡 Idea {i+1}: {idea['title']}", expanded=False):
                if idea['summary']: st.markdown(f"**Summary:** {idea['summary']}")
                if idea['tech_stack']: st.markdown(f"**Tech Stack:** {idea['tech_stack']}")
                st.markdown("---")
                
                if st.button(f"📝 Generate Required Contents", key=f"content_{i}"):
                    
                    with st.spinner("🔍 Extracting keywords..."):
                        keywords = extract_keywords_from_text(f"{idea['title']}. {idea['summary']}")
                        st.info(f"🔑 Keywords: {keywords}")
                        
                        # GitHub Search
                        github_results = []
                        try:
                            q = keywords.replace(',', ' ').strip()
                            url = f"https://api.github.com/search/repositories?q={q}+stars:>100&sort=stars&order=desc&per_page=5"
                            headers = {"Accept": "application/vnd.github+json"}
                            if "github_token" in st.secrets: headers["Authorization"] = f"token {st.secrets['github_token']}"
                            resp = requests.get(url, headers=headers, timeout=10)
                            if resp.status_code == 200:
                                items = resp.json().get("items", [])
                                for item in items:
                                    github_results.append({
                                        "name": item.get("name"), "url": item.get("html_url"),
                                        "description": item.get("description"), "stars": item.get("stargazers_count"),
                                        "language": item.get("language")
                                    })
                        except: pass
                        
                        if github_results:
                            st.markdown("#### 🔗 GitHub Repositories:")
                            for r in github_results:
                                st.markdown(f"- **[{r['name']}]({r['url']})** ({r['language']}) - ⭐ {r['stars']}")
                        
                        # Literature Review
                        st.markdown("#### 📚 Literature Review:")
                        q_url = keywords.replace(',', ' ').replace(' ', '+')
                        st.markdown(f"- [Google Scholar](https://scholar.google.com/scholar?q={q_url})")
                        st.markdown(f"- [arXiv](https://arxiv.org/search/?query={q_url})")
                        
                        # Content Gen
                        with st.spinner("📄 Generating docs..."):
                            prompt = f"Generate project docs for: {idea['title']}. Summary: {idea['summary']}. Tech: {idea['tech_stack']}. Sections: Overview, Problem, Solution, Architecture, Requirements, Impact, Future."
                            resp = client.chat.completions.create(
                                model="gpt-4o", messages=[
                                    {"role": "system", "content": "You are a tech writer."},
                                    {"role": "user", "content": prompt}
                                ], temperature=0.7
                            )
                            content_text = resp.choices[0].message.content.strip()
                            st.markdown("#### 📄 Generated Docs")
                            st.markdown(content_text)
                            st.download_button("💾 Download", content_text, f"{idea['title']}.md")

    # Footer
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #666;'>🚀 Powered by OpenAI GPT-4 | Built with Streamlit</div>", unsafe_allow_html=True)