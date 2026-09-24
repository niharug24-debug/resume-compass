# Understand the project before putting it on your resume

## A 45-second introduction

“I built Resume Compass, a local web application that compares a resume with a job description. The frontend uses HTML, CSS and JavaScript, and the backend uses Python and FastAPI. I extract PDF text with pypdf, identify skills with a predefined dictionary, and calculate the percentage of job skills mentioned in the resume. SQLite stores previous analyses. The application also offers simple wording changes that the user reviews. The score is a keyword comparison, not a real ATS result.”

## Questions you should be able to answer

**Why did you build it?** To practice connecting a form, a Python API, a text processing function and a database in one understandable application.

**Why FastAPI?** It maps Python functions to HTTP endpoints and uses Pydantic for request validation. `/docs` provides interactive API documentation. This app does not need a separate Node server.

**Why plain JavaScript instead of React?** This version has one main form and a few result panels. DOM methods and fetch are sufficient and helped me learn browser fundamentals first.

**What happens after clicking Compare?** JavaScript sends a POST request containing JSON. Pydantic checks input lengths. `analyze()` extracts skills, compares sets, and calculates a result. The backend saves the inputs and result, then returns JSON. JavaScript displays it using textContent.

**How is the score calculated?** If a job mentions Python, SQL, Git and Docker, and the resume mentions the first three, the score is round(3 / 4 × 100) = 75%. Repetition does not increase it because sets contain unique values.

**What are sets and why use them?** A set stores unique elements. Intersection gives matched skills; set difference gives missing skills. Sorting the result makes its display consistent.

**How do aliases work?** The dictionary maps spellings such as `reactjs` and `react.js` to the canonical name React. Each canonical skill counts once.

**Why regular expressions?** Substring searches can incorrectly match Java inside JavaScript. The pattern checks surrounding characters and escapes punctuation so C++ and .NET work. These boundaries are a practical rule, not full language understanding.

**What if no skills are recognized?** The denominator is zero, so the function returns None. JSON encodes it as null and the browser displays N/A rather than a misleading score.

**Is this AI or NLP?** It is basic rule-based text processing. It does not call an AI model or train a machine-learning model. The two wording rules replace “Made” with “Created” and “Worked on” with “Contributed to”. They cannot judge the quality of a resume.

**Does a missing skill mean the applicant does not have it?** No. It only means the supported skill spellings were not found in the resume text.

**How do you read a PDF?** The browser sends raw PDF bytes. The backend limits size, checks the PDF header and parses the data using pypdf. It rejects encrypted files, excessive pages and files without enough extractable text. Scanned pages require OCR, which this project does not include.

**Why SQLite?** It persists data in one file and needs no separate database server. That is enough for a local demo. SQLite is relational; I use one table containing the report ID, title, date, input texts and result JSON.

**How do you prevent SQL injection?** SQL uses question-mark placeholders, with user values passed separately. I never concatenate user input into SQL statements.

**Why a UUID?** It is a convenient unique report identifier. It is not authentication or access control.

**How do you handle errors?** The backend returns HTTP errors with helpful messages; the frontend checks response.ok and shows the message. Validation failures use 422, unreadable input uses 400, oversized files use 413, and missing reports use 404.

**How do you avoid HTML injection?** Document and report strings go into textContent or textarea.value instead of innerHTML. This keeps document text from becoming executable markup.

**Why async on extraction but not analysis?** Extraction awaits the request stream. The analysis/database routes are synchronous because their work is synchronous. PDF parsing itself remains synchronous and can block the extraction handler; a production version should isolate heavy parsing.

**How did you test it?** Unit tests cover matching, aliases, punctuation, determinism and zero-skill input. FastAPI TestClient tests the upload-analysis-save-reopen-delete flow using generated PDFs and a temporary database. Other tests cover malformed, blank, oversized and encrypted PDFs. Read VERIFICATION.md for what was actually run.

**What are the biggest limitations?** Dictionary coverage, no contextual understanding, no OCR, no login and no real AI. The score also treats every recognized skill equally. These are deliberate limits of this local learning version.

**What would you improve next?** Add tests for more skill spellings, distinguish required and preferred skills, then consider login and per-user ownership. Real AI should remain optional, never invent claims, and require clear consent before sending resume text externally.

## Practice by changing the project yourself

1. Add MongoDB and two aliases; write a test that counts it once.
2. Calculate a 2-out-of-3 score by hand and compare the output.
3. Explain each line in `find_skills()` without reading this guide.
4. Follow one request from the submit handler to the SQLite INSERT and back.
5. Restart the app and reopen a saved report to demonstrate persistence.
6. Upload a blank PDF and explain why it cannot be analyzed.

Nobody can guarantee every interview question. If asked about an unimplemented feature, say so and explain how you would investigate it. Avoid memorizing terms that you cannot demonstrate in this code.

## Accurate resume entry

**Resume Compass — Resume Keyword Analyzer | Python, FastAPI, SQLite, JavaScript**

- Built a local web app to extract text from PDF resumes and compare recognized skills with job descriptions using deterministic keyword matching.
- Implemented SQLite analysis history, PDF validation, reviewable rule-based wording suggestions and text export.
- Added automated tests for matching edge cases, invalid PDFs and report persistence/deletion.

Use these bullets only after you can run and explain the project. Do not call it an AI-driven optimizer or claim hiring improvements, ATS accuracy, user counts, or speed gains without evidence.
