🚀 AI Hackathon Idea Generator
💡 Overview

Ever stared blankly at your teammates during a hackathon wondering what to build?
This project solves that!

The AI Hackathon Idea Generator reads hackathon themes, compares them with hundreds of real project ideas, and gives you:

Ready-to-build project ideas

Related GitHub repositories

Sample pitch slides

Insights on how similar ideas performed and the feedback they received

Instead of just brainstorming from scratch, this system learns from real hackathon feedback, evaluator reviews, and project gaps, then generates new ideas grounded in real-world relevance and innovation.

⚙️ Features

🧠 AI-based theme matching

📊 Trained using past hackathon feedback data

💬 Shows previous project insights & evaluator comments

🚀 Generates ready-to-build project ideas with repo and slide links

🌐 Built with Streamlit for easy web-based interaction

🧩 Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/your-username/ai-hackathon-idea-generator.git
cd ai-hackathon-idea-generator

2️⃣ Create a virtual environment
python -m venv venv

3️⃣ Activate the virtual environment

Windows:

venv\Scripts\activate


Mac/Linux:

source venv/bin/activate

4️⃣ Install dependencies
pip install -r requirements.txt

5️⃣ Add your OpenAI API key

Create a .env file in the root directory and add:

OPENAI_API_KEY=your_api_key_here

6️⃣ Run the app
streamlit run app.py

🧠 Future Scope

Add user submissions to continuously improve the dataset

Integrate with GitHub API for live repo fetching

Rank ideas by innovation, feasibility, and technical depth


