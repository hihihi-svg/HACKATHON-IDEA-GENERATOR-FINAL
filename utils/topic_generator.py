import streamlit as st
from openai import OpenAI

import os

# Initialize OpenAI client
# Initialize OpenAI client
try:
    api_key = st.secrets["openai_api_key"]
except:
    api_key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def generate_hackathon_ideas(summary, retrieved_topics, repo_results):
    """
    Generates innovative hackathon project ideas based on the summary, topics, and resources.
    Forces output in markdown table format.
    """
    try:
        # Format retrieved topics
        if isinstance(retrieved_topics, list):
            topics_text = "\n".join([f"- {topic}" for topic in retrieved_topics])
        else:
            topics_text = str(retrieved_topics)
        
        # Format resources (can be GitHub repos or other resources)
        if isinstance(repo_results, list):
            repos_text = "\n".join([
                f"- {repo.get('name', 'Unknown')}: {repo.get('description', 'No description')}"
                for repo in repo_results[:5]
            ])
        else:
            repos_text = str(repo_results)
        
        # Build context
        context = f"""
Competition Summary:
{summary}

Relevant Internal Topics:
{topics_text if topics_text else "No specific topics available"}

Related Resources:
{repos_text if repos_text else "No resources found"}
"""

        prompt = f"""
You are an expert hackathon mentor with deep knowledge of cutting-edge technologies.
Given the following context, generate 5 innovative and feasible hackathon ideas.

Each idea must include:
- Title (catchy and descriptive)
- Short summary (2-3 sentences)
- Suggested tech stack (specific technologies/frameworks)
- 1 example GitHub repo (if available from context)
- Novelty rating (🔥 x1–5, where 5 is most innovative)

IMPORTANT: You MUST output as a proper markdown table format with pipes (|) separating columns.
Use this exact format:

| Title | Summary | Tech Stack | Example Repo | Novelty |
|-------|---------|------------|--------------|---------|
| Project Name Here | Description here | Technologies here | Repo link or N/A | 🔥🔥🔥 |

DO NOT use dashes (---) for table separators in the first column. Use proper markdown table syntax only.

Context:
{context}
"""


        response = client.chat.completions.create(
            model="gpt-4o",  # Use "gpt-4o-mini" for cost savings
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative and experienced hackathon mentor who generates innovative, technically feasible project ideas that align with competition themes and current tech trends. You always format your output as proper markdown tables."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,  # Higher creativity for idea generation
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"❌ Error generating hackathon ideas: {str(e)}"


def generate_hackathon_ideas_structured(summary, retrieved_topics, repo_results):
    """
    Alternative version that returns ideas in a more structured format.
    Useful if you want to parse and display ideas differently.
    """
    try:
        # Format inputs
        if isinstance(retrieved_topics, list):
            topics_text = "\n".join([f"- {topic}" for topic in retrieved_topics])
        else:
            topics_text = str(retrieved_topics)
        
        if isinstance(repo_results, list):
            repos_text = "\n".join([
                f"- {repo.get('name', 'Unknown')}: {repo.get('url', repo.get('html_url', ''))}"
                for repo in repo_results[:5]
            ])
        else:
            repos_text = str(repo_results)
        
        prompt = f"""
Based on this hackathon context, generate 5 innovative project ideas.

Competition Summary: {summary}
Available Topics: {topics_text}
Related Resources: {repos_text}

Format each idea as:
## Idea N: [Title]
**Summary:** [2-3 sentence description]
**Tech Stack:** [Comma-separated list]
**Inspiration Resource:** [URL if available]
**Innovation Level:** [🔥 x1-5]
**Implementation Complexity:** [Easy/Medium/Hard]

---
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # More cost-effective for structured output
            messages=[
                {
                    "role": "system",
                    "content": "You are a hackathon expert who creates practical, innovative project ideas."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"❌ Error generating structured ideas: {str(e)}"