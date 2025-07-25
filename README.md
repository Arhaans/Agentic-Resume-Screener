﻿
# 💼 AI Resume Screener

![AI Resume Screener Frontend](assets/frontend_img.png)

An end-to-end **multi-agent** screening pipeline that ingests a Resume PDF (or URL) and a Job Description (PDF/MD/TXT or URL), runs RAG-powered “Experience” and “Skill” agents via Google Gemini + Pinecone, orchestrates them with LangGraph, and returns a final Interview / Escalate / Reject decision. Includes both a CLI and a React + FastAPI web UI.


---

## 🚀 Features
- ✅ **Dynamic Job Description Support**  
  Upload job descriptions in **PDF**, **Markdown**, or **TXT** format.  
- 🧠 **RAG-Powered Resume Retrieval**  
  - Chunks resume PDF  
  - Embeds using **Sentence-Transformers**  
  - Indexes in **Pinecone**  
  - Retrieves relevant snippets for analysis  
- 🤖 **Multi-Agent Workflow**  
  - `ExperienceAgent`: Classifies as Entry / Mid / Senior  
  - `SkillAgent`: Matches skills vs. JD  
  - `HRDecisionAgent`: Final decision → Interview / Escalate / Reject  
- 🔁 **LangGraph Orchestration**  
  - Declarative, stateful graph of agents  
  - Easy to extend or modify workflows  
- 🌐 **Web Frontend**  
  -   Drag-and-drop or URL inputs, polished card UI 


---

## 📋 Prerequisites

- **Python 3.9+**  
- **Node.js 16+** & npm  
- **Conda** (or virtualenv)  
- A **Google Gemini** API key (`GOOGLE_API_KEY`)  
- A **Pinecone** API key (`PINECONE_API_KEY`)

---

## ⚙️ Installation & Usage
```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/ai-resume-screener.git
cd ai-resume-screener

# 2. Create & activate virtual environment
conda create -n langgraph-env python=3.10 -y
conda activate langgraph-env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Running Backend
uvicorn server:app --reload

# 5. Running Frontend

cd frontend
npm install
npm run dev

# Open your browser to http://localhost:3000.
# Upload Resume (PDF) and JD (PDF/MD/TXT)
# View Experience Level, Skill Match, and Final Verdict

# Example Output:
# Experience Level: Mid-level
# Skill Match:      Match
# Final Response:   Candidate has been shortlisted for an HR interview.


```




## 📂 Project Structure

```bash
Resume-Screener/
├── .env
├── requirements.txt       # Python dependencies
├── main.py                # CLI entry-point & LangGraph orchestration
├── server.py              # FastAPI backend (+ JD URL & HTML scraping)
├── README.md
├── frontend/              # React + Vite web UI
│   ├── package.json
│   ├── vite.config.js     # proxy /api → FastAPI
│   └── src/
│       ├── App.jsx        # Upload form (file or URL)
│       └── App.css        # Card UI styling
└── agents/                # Agent implementations
    ├── resume_agent.py    # PDF chunking, Pinecone indexing & retriever
    ├── jd_loader.py       # (if used) plain JD loader
    ├── experience_agent.py
    ├── skill_agent.py
    ├── hr_decision_agent.py
    └── outcome_agents.py

```


## 🛠️ How It Works
### 🔍 ResumeAgent

- Chunks the uploaded PDF using PyMuPDF or similar tools.

- Embeds the chunks using Sentence-Transformers.

- Stores the embeddings in Pinecone for vector-based retrieval.

- Exposes a retrieve(query) function to fetch relevant text snippets based on a prompt.

### 📝 JDLoader
- Accepts PDF, Markdown, or Text job description files.

- Extracts and cleans text for agent use.

### 🤖 Agents
#### ExperienceAgent
- Uses RAG-style prompting with Google Gemini.

- Labels the candidate as Entry-level, Mid-level, or Senior-level based on resume context.

#### SkillAgent
- Compares relevant resume sections to the JD requirements.
- Outputs either Match or No Match.

#### HRDecisionAgent
- Implements conditional routing logic:

- If Skill Match → Interview

- If Mid/Senior + No Match → Escalate

- Else → Reject

### 🔁 LangGraph Orchestration
- Each agent is a node in a directed graph.

- The flow is managed declaratively using LangGraph.

- A shared state dictionary is passed between nodes, enabling memory and branching.

### 🌐 React Web UI
- Provides a browser-based upload interface.

- React form for file/URL inputs, displays results in a styled card
