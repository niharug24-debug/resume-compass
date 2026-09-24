import io
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

import database
from main import app
from matcher import analyze, find_skills


def pdf(text=None, pages=1, password=None):
    writer = PdfWriter()
    for _ in range(pages):
        page = writer.add_blank_page(width=600, height=800)
        if text:
            font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                                     NameObject('/Subtype'): NameObject('/Type1'),
                                     NameObject('/BaseFont'): NameObject('/Helvetica')})
            page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
            stream = DecodedStreamObject()
            stream.set_data(f'BT /F1 12 Tf 50 750 Td ({text}) Tj ET'.encode())
            page[NameObject('/Contents')] = writer._add_object(stream)
    if password:
        writer.encrypt(password)
    buffer = io.BytesIO(); writer.write(buffer)
    return buffer.getvalue()


class MatchingTests(unittest.TestCase):
    def test_technology_boundaries(self):
        skills = find_skills('C++ C# .NET Node.js React.js REST APIs machine learning')
        self.assertEqual(skills, {'C++', 'C#', '.NET', 'Node.js', 'React', 'REST API', 'Machine learning'})
        self.assertEqual(find_skills('JavaScript GitHub excellent'), {'JavaScript'})

    def test_score_unique_and_deterministic(self):
        result = analyze('Python and SQL projects', 'Python PYTHON SQL Docker')
        self.assertEqual(result['score'], 67)
        self.assertEqual(result['total'], 3)
        self.assertEqual(result, analyze('Python and SQL projects', 'Python PYTHON SQL Docker'))

    def test_zero_skills(self):
        self.assertIsNone(analyze('anything', 'a friendly workplace')['score'])

    def test_suggestions_preserve_evidence(self):
        resume = 'Made a Python app.\nWorked on a class project.'
        for suggestion in analyze(resume, 'Python')['suggestions']:
            self.assertIn(suggestion['original'], resume)
        self.assertEqual(analyze('Built an app.', 'Python')['suggestions'], [])


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_path = database.DB_PATH
        database.DB_PATH = Path(self.temp.name) / 'reports.db'
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        database.DB_PATH = self.old_path
        self.temp.cleanup()

    def upload(self, content):
        return self.client.post('/api/extract', content=content, headers={'Content-Type': 'application/pdf'})

    def test_full_flow_and_persistence(self):
        response = self.upload(pdf('Made a Python student database using SQL and Git.'))
        self.assertEqual(response.status_code, 200)
        created = self.client.post('/api/analyses', json={'resume': response.json()['text'],
            'job': 'Looking for Python, SQL, Git and Docker skills.', 'title': 'Junior developer'})
        self.assertEqual(created.status_code, 201)
        report = created.json()
        self.assertEqual(report['result']['score'], 75)
        # A fresh connection/client reads the same on-disk report.
        with TestClient(app) as fresh:
            self.assertEqual(fresh.get('/api/analyses/' + report['id']).json(), report)
        self.assertEqual(len(self.client.get('/api/analyses').json()), 1)
        self.assertEqual(self.client.delete('/api/analyses/' + report['id']).status_code, 204)
        self.assertEqual(self.client.get('/api/analyses/' + report['id']).status_code, 404)
        self.assertEqual(self.client.get('/api/analyses').json(), [])

    def test_invalid_pdf(self):
        for content in [b'', b'not pdf', b'%PDF-broken']:
            self.assertEqual(self.upload(content).status_code, 400)

    def test_pdf_limits_and_empty_encrypted(self):
        self.assertEqual(self.upload(b'%PDF-' + b'a' * (5 * 1024 * 1024)).status_code, 413)
        self.assertEqual(self.upload(pdf(pages=11)).status_code, 400)
        self.assertEqual(self.upload(pdf()).status_code, 400)
        self.assertEqual(self.upload(pdf(password='secret')).status_code, 400)

    def test_validation_and_unknown_id(self):
        self.assertEqual(self.client.post('/api/extract', content=b'abc').status_code, 415)
        self.assertEqual(self.client.post('/api/analyses', json={'resume':' '*30, 'job':' '*30}).status_code, 422)
        self.assertEqual(self.client.delete('/api/analyses/missing').status_code, 404)

    def test_frontend_and_health(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/static/app.js').status_code, 200)
        self.assertEqual(self.client.get('/health').json()['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
