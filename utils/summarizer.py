import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

def summarize_text(text):
    """
    Summarizes the hackathon/competition description using OpenAI's latest API.
    """
    if not text or len(text.strip()) == 0:
        return "⚠️ Please provide a hackathon description to summarize."
    
    try:
        prompt = f"Summarize this competition or hackathon text briefly in 3-4 lines:\n\n{text}"
        
        response = client.chat.completions.create(
            model="gpt-4o",  # Use "gpt-4o-mini" for faster/cheaper responses
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing and summarizing hackathon and competition descriptions concisely."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,  # Lower temperature for more focused summaries
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"❌ Error during summarization: {str(e)}"