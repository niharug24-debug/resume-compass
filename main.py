"""Run with: python -m uvicorn main:app --host 127.0.0.1 --port 8000"""
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from pypdf import PdfReader
from starlette.middleware.trustedhost import TrustedHostMiddleware

import database
from matcher import analyze

app = FastAPI(title='Resume Compass — local learning project')
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', 'testserver'])
STATIC = Path(__file__).parent / 'static'
MAX_PDF_BYTES = 5 * 1024 * 1024
app.mount('/static', StaticFiles(directory=STATIC), name='static')


class AnalysisInput(BaseModel):
    title: str = Field(default='Untitled role', max_length=100)
    resume: str = Field(min_length=20, max_length=30000)
    job: str = Field(min_length=20, max_length=15000)

    @field_validator('resume', 'job')
    @classmethod
    def meaningful_text(cls, value):
        if len(value.strip()) < 20:
            raise ValueError('Please enter at least 20 characters of text.')
        return value.strip()


@app.get('/')
def home():
    return FileResponse(STATIC / 'index.html')


@app.get('/health')
def health():
    return {'status': 'ok', 'mode': 'local-single-user'}


@app.post('/api/extract')
async def extract(request: Request):
    # Raw PDF body avoids multipart complexity; cap the bytes while reading.
    if request.headers.get('content-type', '').split(';')[0] != 'application/pdf':
        raise HTTPException(415, 'Choose a PDF file.')
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > MAX_PDF_BYTES:
            raise HTTPException(413, 'The PDF must be 5 MB or smaller.')
    if not data.startswith(b'%PDF-'):
        raise HTTPException(400, 'This file is not a valid PDF.')
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise HTTPException(400, 'Use a PDF without password protection.')
        if len(reader.pages) > 10:
            raise HTTPException(400, 'Use a resume with no more than 10 pages.')
        text = '\n\n'.join(page.extract_text() or '' for page in reader.pages).strip()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(400, 'The PDF could not be read. Export a new PDF and retry.') from None
    if len(text) < 20:
        raise HTTPException(400, 'No usable text found. Scanned PDFs need OCR; paste your text instead.')
    if len(text) > 30000:
        raise HTTPException(400, 'Extracted text is too long. Use a shorter resume.')
    return {'text': text}


@app.post('/api/analyses', status_code=201)
def create_analysis(body: AnalysisInput):
    report = {'id': str(uuid4()), 'title': body.title.strip() or 'Untitled role',
              'created_at': datetime.now(timezone.utc).isoformat(),
              'resume': body.resume, 'job': body.job, 'result': analyze(body.resume, body.job)}
    database.save(report)
    return report


@app.get('/api/analyses')
def list_analyses():
    return database.history()


@app.get('/api/analyses/{report_id}')
def get_analysis(report_id: str):
    report = database.get(report_id)
    if report is None:
        raise HTTPException(404, 'Report not found.')
    return report


@app.delete('/api/analyses/{report_id}', status_code=204)
def delete_analysis(report_id: str):
    if not database.delete(report_id):
        raise HTTPException(404, 'Report not found.')
