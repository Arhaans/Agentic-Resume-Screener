# # server.py

# import os
# import tempfile
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# from main import run_multiagent_screening
# import uvicorn

# load_dotenv()

# app = FastAPI()
# # allow your React dev server (http://localhost:3000) to talk to us
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # in prod lock this down
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.post("/api/screen")
# async def screen(
#     resume: UploadFile = File(...),
#     jd: UploadFile     = File(...)
# ):
#     # 1️⃣ Validate types
#     if resume.content_type != "application/pdf":
#         raise HTTPException(400, "Resume must be a PDF")
#     ext = os.path.splitext(jd.filename)[1].lower()
#     if ext not in (".pdf", ".md", ".txt"):
#         raise HTTPException(400, "JD must be PDF/MD/TXT")

#     # 2️⃣ Save to temp files
#     try:
#         with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_res:
#             tmp_res.write(await resume.read())
#             resume_path = tmp_res.name

#         with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_jd:
#             tmp_jd.write(await jd.read())
#             jd_path = tmp_jd.name

#         # 3️⃣ Run your multi-agent pipeline
#         result = run_multiagent_screening(
#             resume_path,
#             jd_path,
#             resume_name=resume.filename
#         )

#     finally:
#         # 4️⃣ Clean up
#         for p in (locals().get("resume_path"), locals().get("jd_path")):
#             if p and os.path.exists(p):
#                 os.unlink(p)

#     return result

# if __name__ == "__main__":
#     uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

# server.py

import os
import tempfile
import requests
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from bs4 import BeautifulSoup     # new import!

from main import run_multiagent_screening

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/screen")
async def screen_resume(
    resume: UploadFile,
    jd: UploadFile = None,
    jd_url: str = Form(None),
):
    resume_path = jd_path = None
    try:
        # 1️⃣ Save resume upload
        if resume.content_type != "application/pdf":
            raise HTTPException(400, "Resume must be PDF")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_res:
            tmp_res.write(await resume.read())
            resume_path = tmp_res.name

        # 2️⃣ Determine JD source: file or URL
        if jd:
            # JD was uploaded
            jd_ext = os.path.splitext(jd.filename)[1].lower()
            if jd_ext not in (".pdf", ".md", ".txt"):
                raise HTTPException(400, "JD file must be PDF/MD/TXT")
            with tempfile.NamedTemporaryFile(suffix=jd_ext, delete=False) as tmp_jd:
                tmp_jd.write(await jd.read())
                jd_path = tmp_jd.name

        elif jd_url:
            # JD URL provided
            resp = requests.get(jd_url)
            if resp.status_code != 200:
                raise HTTPException(400, f"Failed to fetch JD URL ({resp.status_code})")

            content_type = resp.headers.get("Content-Type", "")
            # 2a) If PDF link
            if "application/pdf" in content_type or jd_url.lower().endswith(".pdf"):
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_jd:
                    tmp_jd.write(resp.content)
                    jd_path = tmp_jd.name

            else:
                # 2b) Otherwise assume HTML/text → parse visible text
                soup = BeautifulSoup(resp.text, "html.parser")
                # remove scripts, styles, nav/footer, etc.
                for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
                    tag.decompose()
                text = soup.get_text(separator="\n").strip()
                if not text:
                    raise HTTPException(400, "No textual content found at JD URL")

                with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_jd:
                    tmp_jd.write(text.encode("utf-8"))
                    jd_path = tmp_jd.name

        else:
            raise HTTPException(400, "Provide either a JD file or JD URL")

        # 3️⃣ Run multi-agent screening
        result = run_multiagent_screening(
            resume_path,
            jd_path,
            resume_name=resume.filename
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Screening error: {e}")

    finally:
        # 4️⃣ Cleanup temp files
        for path in (resume_path, jd_path):
            try:
                if path and os.path.exists(path):
                    os.unlink(path)
            except:
                pass
