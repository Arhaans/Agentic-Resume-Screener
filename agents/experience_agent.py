from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

def experience_agent(llm: ChatPromptTemplate | ChatGoogleGenerativeAI, retriever) -> str:
    """
    Returns *only* one of: "Entry-level", "Mid-level", or "Senior-level".
    """
    # 1️⃣ Retrieve context from resume
    context = retriever.retrieve("Categorize overall experience level")

    # 2️⃣ Prompt with an explicit instruction for a single-label response
    prompt = ChatPromptTemplate.from_template(
        "Resume context:\n{context}\n\n"
        "Question: Categorize this candidate’s overall experience level.\n"
        "Answer *only* with exactly one of: Entry-level, Mid-level, Senior-level."
    )
    chain = prompt | llm

    # 3️⃣ Invoke and clean up
    raw = chain.invoke({"context": context}).content.strip()
    # Look for one of the three labels in the raw text
    for label in ("Entry-level", "Mid-level", "Senior-level"):
        if label.lower() in raw.lower():
            return label
    # Fallback
    return raw.splitlines()[0].strip()
