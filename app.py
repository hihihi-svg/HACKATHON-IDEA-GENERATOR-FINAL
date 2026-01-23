import streamlit as st
import re
import requests
from openai import OpenAI
from utils.summarizer import summarize_text
from utils.retriever import create_vector_db, retrieve_relevant_topics
from utils.resource_finder import find_relevant_resources
from utils.topic_generator import generate_hackathon_ideas

# ✅ Initialize OpenAI client with latest API
client = OpenAI(api_key=st.secrets["openai_api_key"])

st.set_page_config(page_title="Hackathon Idea Generator", page_icon="🚀", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Hackathon Idea Generator")
st.markdown("Generate innovative project ideas using your hackathon description and uploaded topics!")

# --- Sidebar ---
st.sidebar.header("📄 Upload Your Topics File (.docx)")
st.sidebar.markdown("Upload a DOCX file containing relevant topics, technologies, or domain knowledge to enhance idea generation.")

uploaded_file = st.sidebar.file_uploader("Upload DOCX", type=["docx"])

if uploaded_file:
    # Save uploaded file
    import os
    import shutil
    os.makedirs("data", exist_ok=True)
    
    with open("data/topics.docx", "wb") as f:
        f.write(uploaded_file.read())
    st.sidebar.success("✅ Topics file uploaded!")
    
    # Add a clear database button
    if st.sidebar.button("🗑️ Clear Old Vector DB"):
        vector_db_path = "vectorstore/chroma_db"
        if os.path.exists(vector_db_path):
            try:
                shutil.rmtree(vector_db_path)
                st.sidebar.success("✅ Old vector database cleared!")
            except Exception as e:
                st.sidebar.error(f"❌ Error clearing database: {e}")
        else:
            st.sidebar.info("ℹ️ No existing database found")

    if st.sidebar.button("🔄 Create Vector DB"):
        with st.spinner("Creating vector database..."):
            # Automatically delete old database before creating new one
            vector_db_path = "vectorstore/chroma_db"
            if os.path.exists(vector_db_path):
                try:
                    shutil.rmtree(vector_db_path)
                    st.sidebar.info("🗑️ Old vector database deleted")
                except Exception as e:
                    st.sidebar.warning(f"⚠️ Could not delete old database: {e}")
            
            # Create new vector database
            create_vector_db("data/topics.docx")
            st.sidebar.success("✅ Vector DB created successfully!")

# Add info section in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ How It Works")
st.sidebar.markdown("""
1. **Upload Topics** (Optional): Add domain knowledge
2. **Enter Hackathon Description**: Paste the competition details
3. **Generate Ideas**: Get AI-powered project suggestions
4. **Generate Content**: Create detailed documentation for each idea
""")

# --- Main Area ---
st.markdown("## 📝 Hackathon Description")
hackathon_text = st.text_area(
    "✍️ Paste your Hackathon / Competition Description", 
    height=150,
    placeholder="Example: Build an AI-powered healthcare solution that helps rural communities access medical diagnosis using mobile devices..."
)

# Create two columns for buttons
col1, col2 = st.columns(2)

with col1:
    summarize_btn = st.button("🧠 Summarize Theme", use_container_width=True)

with col2:
    generate_btn = st.button("✨ Generate Ideas", use_container_width=True, type="primary")

# Summarize Theme
if summarize_btn:
    if not hackathon_text:
        st.warning("⚠️ Please enter a hackathon description first.")
    else:
        with st.spinner("Analyzing theme..."):
            summary = summarize_text(hackathon_text)
            st.session_state["summary"] = summary
            
            st.markdown("### 🧠 Summarized Theme")
            st.info(summary)

# Generate Ideas
if generate_btn:
    if not hackathon_text:
        st.warning("⚠️ Please enter a hackathon description first.")
    else:
        with st.spinner("🔍 Analyzing and generating innovative ideas..."):
            # Step 1: Summarize
            summary = summarize_text(hackathon_text)
            st.session_state["summary"] = summary
            
            # Step 2: Retrieve relevant topics from vector DB
            retrieved_topics = retrieve_relevant_topics(summary)
            
            # Step 3: Find relevant resources (for context in generation)
            resources = find_relevant_resources(summary)
            
            # Step 4: Generate hackathon ideas (force table format)
            ideas = generate_hackathon_ideas(summary, retrieved_topics, resources)
            
            # Store in session state
            st.session_state["raw_ideas"] = ideas
            
            # Display the ideas table
            st.markdown("---")
            st.markdown("## 💡 Generated Hackathon Ideas")
            st.markdown(ideas)
            
            # --- Extract ideas with descriptions from the generated content ---
            # Parse the markdown table or list to extract idea details
            lines = ideas.split('\n')
            parsed_ideas = []
            
            # Try to parse markdown table format
            for line in lines:
                if '|' in line and not line.strip().startswith('|---'):
                    cells = [cell.strip() for cell in line.split('|')]
                    cells = [c for c in cells if c]  # Remove empty cells
                    
                    # Skip header row
                    if cells and cells[0].lower() not in ['title', 'summary', 'tech stack', 'example repo', 'novelty', 'innovation level']:
                        if len(cells) >= 2:  # At least title and summary
                            parsed_ideas.append({
                                'title': cells[0],
                                'summary': cells[1] if len(cells) > 1 else '',
                                'tech_stack': cells[2] if len(cells) > 2 else '',
                            })
            
            # Fallback: Extract numbered ideas if table parsing fails
            if not parsed_ideas:
                title_pattern = r'(?:\d+\.\s*\*\*|###?\s*)([^:\n]+)'
                titles = re.findall(title_pattern, ideas)
                for title in titles[:5]:
                    parsed_ideas.append({
                        'title': title.strip('*').strip(),
                        'summary': '',
                        'tech_stack': ''
                    })
            
            st.session_state["parsed_ideas"] = parsed_ideas[:5]

def extract_keywords_from_text(text):
    """
    Extract important keywords from the idea description using OpenAI.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a keyword extraction expert. Extract 3-5 key technical terms or concepts from the given text. Return only comma-separated keywords, nothing else."
                },
                {
                    "role": "user",
                    "content": f"Extract keywords from: {text}"
                }
            ],
            temperature=0.3,
            max_tokens=50
        )
        keywords = response.choices[0].message.content.strip()
        return keywords
    except:
        return text[:50]  # Fallback to first 50 chars

# --- Show Ideas + Required Content Generation ---
if "parsed_ideas" in st.session_state and st.session_state["parsed_ideas"]:
    ideas_list = st.session_state["parsed_ideas"]
    
    st.markdown("---")
    st.markdown("## 📋 Generate Required Contents")
    st.markdown("Create detailed documentation and GitHub resources for each generated idea:")

    for i, idea in enumerate(ideas_list):
        idea_title = idea['title']
        idea_summary = idea['summary']
        idea_tech = idea['tech_stack']
        
        with st.expander(f"💡 Idea {i+1}: {idea_title}", expanded=False):
            
            # Show idea details
            if idea_summary:
                st.markdown(f"**Summary:** {idea_summary}")
            if idea_tech:
                st.markdown(f"**Tech Stack:** {idea_tech}")
            
            st.markdown("---")
            
            # Generate required content button
            if st.button(f"📝 Generate Required Contents", key=f"content_{i}"):
                with st.spinner("🔍 Extracting keywords and searching resources..."):
                    
                    # Extract keywords from THIS SPECIFIC IDEA (title + summary)
                    # NOT from the original hackathon description
                    search_text = f"{idea_title}. {idea_summary}"
                    keywords = extract_keywords_from_text(search_text)
                    
                    st.info(f"🔑 Extracted Keywords: {keywords}")
                    
                    # Search GitHub based on extracted keywords
                    github_results = []
                    
                    try:
                        # GitHub search API
                        search_query = keywords.replace(',', ' ').strip()
                        url = f"https://api.github.com/search/repositories?q={search_query}+stars:>100&sort=stars&order=desc&per_page=5"
                        
                        headers = {"Accept": "application/vnd.github+json"}
                        if "github_token" in st.secrets:
                            headers["Authorization"] = f"token {st.secrets['github_token']}"
                        
                        response = requests.get(url, headers=headers, timeout=10)
                        
                        if response.status_code == 200:
                            items = response.json().get("items", [])
                            for item in items[:5]:
                                github_results.append({
                                    "name": item.get("name", ""),
                                    "url": item.get("html_url", ""),
                                    "description": item.get("description", "No description"),
                                    "stars": item.get("stargazers_count", 0),
                                    "language": item.get("language", "N/A")
                                })
                    except Exception as e:
                        st.warning(f"⚠️ Could not fetch GitHub results: {str(e)}")
                    
                    if github_results:
                        st.markdown("#### 🔗 GitHub Repositories:")
                        for repo in github_results:
                            st.markdown(f"- **[{repo['name']}]({repo['url']})** ({repo['language']}) - ⭐ {repo['stars']:,}")
                            st.caption(repo['description'])
                    else:
                        st.info("No GitHub repositories found for these keywords.")
                    
                    st.markdown("---")
                    
                    # Generate Literature Review Resources
                    st.markdown("#### 📚 Literature Review Resources:")
                    
                    # Prepare search query for URLs
                    search_query_encoded = keywords.replace(',', ' ').replace(' ', '+').strip()
                    
                    literature_resources = [
                        {
                            "name": "Google Scholar",
                            "url": f"https://scholar.google.com/scholar?q={search_query_encoded}",
                            "description": "Academic papers and research articles",
                            "icon": "📚"
                        },
                        {
                            "name": "arXiv.org",
                            "url": f"https://arxiv.org/search/?query={search_query_encoded}&searchtype=all",
                            "description": "Latest preprints and research papers",
                            "icon": "📄"
                        },
                        {
                            "name": "IEEE Xplore",
                            "url": f"https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={search_query_encoded}",
                            "description": "Technical literature and conference papers",
                            "icon": "🔬"
                        },
                        {
                            "name": "ResearchGate",
                            "url": f"https://www.researchgate.net/search?q={search_query_encoded}",
                            "description": "Research papers and academic publications",
                            "icon": "🎓"
                        },
                        {
                            "name": "Wikipedia",
                            "url": f"https://en.wikipedia.org/wiki/Special:Search?search={search_query_encoded}",
                            "description": "General background and foundational knowledge",
                            "icon": "📖"
                        },
                        {
                            "name": "Medium Articles",
                            "url": f"https://medium.com/search?q={search_query_encoded}",
                            "description": "Developer articles and practical tutorials",
                            "icon": "✍️"
                        }
                    ]
                    
                    for resource in literature_resources:
                        st.markdown(f"- {resource['icon']} **[{resource['name']}]({resource['url']})** - {resource['description']}")
                    
                    st.markdown("---")
                
                with st.spinner("📄 Generating required content documentation..."):
                    prompt = f"""
                    You are a hackathon documentation expert. Generate comprehensive required content for the project idea: "{idea_title}".
                    
                    Summary: {idea_summary}
                    Tech Stack: {idea_tech}
                    
                    Create detailed documentation with the following sections:
                    
                    1. **Project Overview** (2-3 sentences)
                       - Brief description of the project
                    
                    2. **Problem Statement** (3-4 points)
                       - What problem does this solve?
                       - Why is it important?
                       - Current limitations or gaps
                    
                    3. **Proposed Solution** (4-5 points)
                       - Your innovative approach
                       - Key features and functionality
                       - How it addresses the problem
                    
                    4. **Technical Architecture** (4-5 points)
                       - System design overview
                       - Main components and their interactions
                       - Data flow and processing
                    
                    5. **Implementation Requirements**
                       - Required technologies and tools
                       - APIs or services needed
                       - Development environment setup
                    
                    6. **Expected Outcomes & Impact** (3-4 points)
                       - Benefits to users/stakeholders
                       - Measurable success metrics
                       - Real-world applications
                    
                    7. **Future Enhancements** (3-4 points)
                       - Scalability considerations
                       - Additional features
                       - Long-term vision
                    
                    Format the output professionally with clear headings and bullet points.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are a professional technical documentation writer who creates comprehensive, well-structured project documentation."
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=2500
                    )

                    content_text = response.choices[0].message.content.strip()
                    
                    st.markdown("#### 📄 Generated Required Contents")
                    st.markdown(content_text)
                    
                    # Add download button
                    full_content = f"""# {idea_title}

## Summary
{idea_summary}

## Tech Stack
{idea_tech}

## Keywords
{keywords}

## GitHub Repositories
{chr(10).join([f"- [{r['name']}]({r['url']}) - {r['language']} (⭐ {r['stars']:,})" for r in github_results]) if github_results else "No GitHub repositories found"}

## Literature Review Resources
- 📚 [Google Scholar](https://scholar.google.com/scholar?q={keywords.replace(',', ' ').replace(' ', '+')})
- 📄 [arXiv.org](https://arxiv.org/search/?query={keywords.replace(',', ' ').replace(' ', '+')}&searchtype=all)
- 🔬 [IEEE Xplore](https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={keywords.replace(',', ' ').replace(' ', '+')})
- 🎓 [ResearchGate](https://www.researchgate.net/search?q={keywords.replace(',', ' ').replace(' ', '+')})
- 📖 [Wikipedia](https://en.wikipedia.org/wiki/Special:Search?search={keywords.replace(',', ' ').replace(' ', '+')})
- ✍️ [Medium Articles](https://medium.com/search?q={keywords.replace(',', ' ').replace(' ', '+')})

---

{content_text}
"""
                    
                    st.download_button(
                        label="💾 Download Complete Documentation",
                        data=full_content,
                        file_name=f"{idea_title[:30].replace(' ', '_')}_documentation.md",
                        mime="text/markdown",
                        key=f"download_{i}"
                    )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🚀 Powered by OpenAI GPT-4 & LangChain | Built with Streamlit</p>
        <p>💡 Generate innovative ideas • 🔗 Find GitHub resources • 📋 Create documentation</p>
    </div>
    """, unsafe_allow_html=True)