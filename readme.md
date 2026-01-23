# 🚀 Hackathon Idea Generator

An AI-powered tool designed to help hackathon teams generate innovative project ideas, detailed documentation, and technical roadmaps instantly.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![OpenAI](https://img.shields.io/badge/AI-OpenAI_GPT-green)
![LangChain](https://img.shields.io/badge/Framework-LangChain-orange)

## 💡 Overview

Staring at a blank screen during a hackathon? This tool solves "builder's block" by generating:
- **Innovative Project Ideas** based on the hackathon theme.
- **Full Documentation** (Problem, Solution, Tech Stack).
- **GitHub Repository Search** for similar existing projects.
- **Literature Review** resources.

It uses **RAG (Retrieval-Augmented Generation)** with ChromaDB to ground ideas in real technical concepts.

## ✨ Key Features

### 🔐 Authentication & User Management
- **Secure Login/Register**: Users must create an account to access the tool.
- **Persistent Credits**: User credits are stored in a database (`users.db`), persisting across sessions.
- **Registration Limit**: Abuse prevention restricts sign-ups to 5 accounts per device/IP.

### 🛡️ Usage Controls (Freemium Model)
- **Trial Limit**: Each user gets **2 FREE generations**.
- **Admin Bypass**: Owner accounts (or those with the Admin Password) get **Unlimited Access**.
- **Zero-Friction**: No need for users to bring their own API keys; the system is centrally managed.

### 🧠 Advanced AI Generation
- **Topic Retrieval**: Fetches relevant domain knowledge from your uploaded `topics.docx`.
- **Structured Output**: Generates tables of ideas with "Innovation Level" and "Novelty" scores.
- **Automated Docs**: Instantly writes a `README.md` style project plan for your chosen idea.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI/LLM**: OpenAI GPT-4o & GPT-4o-mini
- **Orchestration**: LangChain
- **Vector DB**: ChromaDB
- **Database**: SQLite (User Auth & Credits)
- **Deployment**: Render

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/hihihi-svg/HACKATHON-IDEA-GENERATOR-FINAL.git
   cd HACKATHON-IDEA-GENERATOR-FINAL
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Secrets**
   Create a `.streamlit/secrets.toml` file:
   ```toml
   openai_api_key = "your-key"
   github_token = "optional-token"
   ADMIN_PASSWORD = "your-admin-password"
   ```

4. **Run the App**
   ```bash
   streamlit run app.py
   ```

## ☁️ Deployment (Render)

This project is configured for one-click deployment on [Render](https://render.com).

1. Connect your GitHub repo.
2. Render will auto-detect the `render.yaml` configuration.
3. Add Environment Variables in the Dashboard:
   - `OPENAI_API_KEY`
   - `ADMIN_PASSWORD`

## ⚖️ Limitations & Future Scope

- **Ephemeral Storage**: On free hosting tiers (like Render Free), the SQLite database resets on redeployment. For production, switch `utils/db.py` to use PostgreSQL/Supabase.
- **Rate Limiting**: Currently capped at 2 trials/user for cost control.
- **Future**: Add team collaboration features and direct "Export to GitHub" functionality.

---
*Built for Hackathon excellence.* 🚀
