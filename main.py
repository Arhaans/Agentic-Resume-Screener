# import os
# from dotenv import load_dotenv

# # Load .env into os.environ
# load_dotenv()

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langgraph.graph import StateGraph, START, END
# from typing_extensions import TypedDict

# from agents.experience_agent import experience_agent
# from agents.skill_agent import skill_agent
# from agents.hr_decision_agent import hr_decision_agent
# from agents.outcome_agents import (
#     interview_agent,
#     escalation_agent,
#     rejection_agent,
# )

# class State(TypedDict):
#     application: str
#     experience_level: str
#     skill_match: str
#     response: str

# # Initialize your LLM
# llm = ChatGoogleGenerativeAI(
#     model="models/gemini-1.5-flash",
#     temperature=0.7,
#     google_api_key=os.getenv("GOOGLE_API_KEY")
# )

# # Build the multi-agent workflow
# workflow = StateGraph(State)

# # 1️⃣ Experience classification
# workflow.add_node(
#     "experience_agent",
#     lambda s: {**s, "experience_level": experience_agent(llm, s["application"])}
# )

# # 2️⃣ Skill assessment
# workflow.add_node(
#     "skill_agent",
#     lambda s: {**s, "skill_match": skill_agent(llm, s["application"])}
# )

# # 3️⃣ Final outcomes
# workflow.add_node("interview_agent",  lambda s: {**s, "response": interview_agent()})
# workflow.add_node("escalation_agent", lambda s: {**s, "response": escalation_agent()})
# workflow.add_node("rejection_agent",  lambda s: {**s, "response": rejection_agent()})

# # Wire up the edges
# workflow.add_edge(START, "experience_agent")
# workflow.add_edge("experience_agent", "skill_agent")

# # Branch based on (experience, skill) → one of our three outcome nodes
# workflow.add_conditional_edges(
#     "skill_agent",
#     lambda s: hr_decision_agent(s["experience_level"], s["skill_match"])
# )

# # End the graph
# workflow.add_edge("interview_agent",  END)
# workflow.add_edge("escalation_agent", END)
# workflow.add_edge("rejection_agent",  END)

# # Compile
# app = workflow.compile()

# def run_multiagent_screening(application: str) -> State:
#     init_state = {
#         "application": application,
#         "experience_level": "",
#         "skill_match": "",
#         "response": ""
#     }
#     return app.invoke(init_state)

# if __name__ == "__main__":
#     sample = "I am a computer science engineer with 10 years of experience and heavy python programming skills"
#     outcome = run_multiagent_screening(sample)
#     print(f"Experience Level: {outcome['experience_level']}")
#     print(f"Skill Match:       {outcome['skill_match']}")
#     print(f"Action Taken:      {outcome['response']}")

# main.py
import os
import sys
from dotenv import load_dotenv
from typing_extensions import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

from agents.resume_agent import (
    index,
    embedder,
    load_and_chunk_pdf_text,
    upsert_to_pinecone,
    PineconeRetriever,
)
from agents.jd_loader import load_job_description
from agents.experience_agent import experience_agent
from agents.skill_agent import skill_agent
from agents.hr_decision_agent import hr_decision_agent
from agents.outcome_agents import (
    interview_agent,
    escalation_agent,
    rejection_agent,
)

# --------------------
# Shared State Schema
# --------------------
class State(TypedDict):
    experience_level: str
    skill_match: str
    response: str

# --------------------
# Runner
# --------------------
def run_multiagent_screening(
    resume_path: str,
    jd_path: str,
    resume_name: str = None
) -> State:
    """
    resume_name: original filename, used to tag metadata.source so
                 PineconeRetriever.filter picks up exactly these chunks.
    """
    # 1️⃣ Determine the 'source' key
    source = resume_name or os.path.basename(resume_path)

    # 2️⃣ Load & chunk the resume PDF
    chunks = load_and_chunk_pdf_text(resume_path)
    # Override each chunk's metadata["source"]
    for chunk in chunks:
        chunk["metadata"]["source"] = source

    # 3️⃣ Upsert into Pinecone
    upsert_to_pinecone(index, chunks)

    # 4️⃣ Build a retriever that filters by this source
    retriever = PineconeRetriever(index, embedder, source)

    # 5️⃣ Load the dynamic job description text
    jd_text = load_job_description(jd_path)

    # 6️⃣ Initialize the HTTP‐only Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash",
        temperature=0.7,
        api_key=os.getenv("GOOGLE_API_KEY")
    )

    # 7️⃣ Build your LangGraph workflow
    workflow = StateGraph(State)
    workflow.add_node(
        "experience_agent",
        lambda s: {**s, "experience_level": experience_agent(llm, retriever)}
    )
    workflow.add_node(
        "skill_agent",
        lambda s: {**s, "skill_match": skill_agent(llm, retriever, jd_text)}
    )
    workflow.add_node(
        "interview_agent",
        lambda s: {**s, "response": interview_agent()}
    )
    workflow.add_node(
        "escalation_agent",
        lambda s: {**s, "response": escalation_agent()}
    )
    workflow.add_node(
        "rejection_agent",
        lambda s: {**s, "response": rejection_agent()}
    )

    workflow.add_edge(START, "experience_agent")
    workflow.add_edge("experience_agent", "skill_agent")
    workflow.add_conditional_edges(
        "skill_agent",
        lambda s: hr_decision_agent(s["experience_level"], s["skill_match"])
    )
    workflow.add_edge("interview_agent", END)
    workflow.add_edge("escalation_agent", END)
    workflow.add_edge("rejection_agent", END)

    app = workflow.compile()
    init_state = {"experience_level": "", "skill_match": "", "response": ""}
    return app.invoke(init_state)

if __name__ == "__main__":
    load_dotenv()
    if len(sys.argv) != 3:
        print("Usage: python main.py path/to/resume.pdf path/to/job_description.{pdf,md,txt}")
        sys.exit(1)

    resume_file, jd_file = sys.argv[1], sys.argv[2]
    result = run_multiagent_screening(
        resume_file,
        jd_file,
        resume_name=os.path.basename(resume_file)
    )

    print("Experience Level:", result["experience_level"])
    print("Skill Match:     ", result["skill_match"])
    print("Final Response:  ", result["response"])
