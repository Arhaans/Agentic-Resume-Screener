// // frontend/src/App.jsx
// import { useState } from 'react'
// import './App.css'

// function App() {
//   const [resume, setResume] = useState(null)
//   const [jd, setJD]         = useState(null)
//   const [result, setResult] = useState(null)
//   const [loading, setLoading] = useState(false)

//   const handleSubmit = async (e) => {
//     e.preventDefault()
//     if (!resume || !jd) return
//     setLoading(true)

//     const formData = new FormData()
//     formData.append('resume', resume)
//     formData.append('jd', jd)

//     try {
//       const resp = await fetch('/api/screen', {
//         method: 'POST',
//         body: formData,
//       })
//       if (!resp.ok) throw new Error(await resp.text())
//       const data = await resp.json()
//       setResult(data)
//     } catch (err) {
//       alert("Error: " + err.message)
//     } finally {
//       setLoading(false)
//     }
//   }

//   return (
//     <div id="container">
//     <div className="App">
//       <h1>AI Resume & JD Screener</h1>
//       <form onSubmit={handleSubmit}>
//         <label>
//           Resume (PDF):
//           <input
//             type="file"
//             accept="application/pdf"
//             onChange={e => setResume(e.target.files[0])}
//             required
//           />
//         </label>
//         <label>
//           Job Description (PDF/MD/TXT):
//           <input
//             type="file"
//             accept=".pdf,.md,.txt"
//             onChange={e => setJD(e.target.files[0])}
//             required
//           />
//         </label>
//         <button type="submit" disabled={loading}>
//           {loading ? 'Screening...' : 'Run Screening'}
//         </button>
//       </form>

//       {result && (
//         <div className="results">
//           <h2>Results</h2>
//           <p><strong>Experience Level:</strong> {result.experience_level}</p>
//           <p><strong>Skill Match:</strong>      {result.skill_match}</p>
//           <p><strong>Final Decision:</strong>  {result.response}</p>
//         </div>
//       )}
//     </div>
//     </div>
//   )
// }

// export default App

// frontend/src/App.jsx

import React, { useState } from 'react';
import './App.css';

function App() {
  const [resume, setResume] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [jdLink, setJdLink] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!resume || (!jdFile && !jdLink)) return;
    setLoading(true);

    const formData = new FormData();
    formData.append('resume', resume);
    if (jdFile) {
      formData.append('jd', jdFile);
    } else {
      formData.append('jd_url', jdLink);
    }

    try {
      const resp = await fetch('/api/screen', {
        method: 'POST',
        body: formData,
      });
      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(text || resp.statusText);
      }
      const data = await resp.json();
      setResult(data);
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>AI Resume & JD Screener</h1>

      <form onSubmit={handleSubmit}>
        <label>
          Resume (PDF):
          <input
            type="file"
            accept="application/pdf"
            onChange={e => { setResume(e.target.files[0]); setResult(null); }}
            required
          />
        </label>

        <label>
          Job Description (PDF/MD/TXT):
          <input
            type="file"
            accept=".pdf,.md,.txt"
            onChange={e => {
              setJdFile(e.target.files[0]);
              setJdLink("");
              setResult(null);
            }}
          />
        </label>

        <label>
          Or paste a Job Description URL:
          <input
            type="url"
            placeholder="https://example.com/job-posting"
            value={jdLink}
            onChange={e => {
              setJdLink(e.target.value);
              setJdFile(null);
              setResult(null);
            }}
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Screening...' : 'Run Screening'}
        </button>
      </form>

      {result && (
        <div className="results">
          <h2>Results</h2>
          <p><strong>Experience Level:</strong> {result.experience_level}</p>
          <p><strong>Skill Match:</strong>      {result.skill_match}</p>
          <p><strong>Final Decision:</strong>  {result.response}</p>
        </div>
      )}
    </div>
  );
}

export default App;
