# agents/skill_agent.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

def skill_agent(
    llm: ChatGoogleGenerativeAI,
    retriever,
    job_description: str
) -> str:
    """
    Returns exactly 'Match' or 'No Match' by comparing
    the resume context against the provided job_description.
    """
    # 1️⃣ Retrieve the relevant resume snippets
    context = retriever.retrieve("Assess candidate against the JD")

    # 2️⃣ If there's no 'python' keyword *and* JD mentions 'Python', quick no-match
    # (optional heuristic, remove if you don't want it)
    if "python" not in context.lower() and "python" in job_description.lower():
        return "No Match"

    # 3️⃣ Build a prompt that includes both JD and resume context
    prompt = ChatPromptTemplate.from_template(
        "Job Description:\n{jd}\n\n"
        "Resume Context:\n{context}\n\n"
        "Question: Does this candidate match the above job description?\n"
        "Answer *only* with exactly one of: Match or No Match."
    )
    chain = prompt | llm

    raw = chain.invoke({"jd": job_description, "context": context}).content.strip().lower()
    return "Match" if "match" in raw else "No Match"
