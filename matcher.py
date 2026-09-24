"""An intentionally small, deterministic engine: no AI or hidden scoring."""
import re

# Canonical name -> accepted spellings. Extend this dictionary to support more roles.
SKILLS = {
    'Python': ['python'], 'Java': ['java'], 'JavaScript': ['javascript', 'js'],
    'TypeScript': ['typescript'], 'HTML': ['html'], 'CSS': ['css'],
    'React': ['react', 'react.js', 'reactjs'], 'Node.js': ['node.js', 'nodejs'],
    'SQL': ['sql'], 'SQLite': ['sqlite'], 'PostgreSQL': ['postgresql', 'postgres'],
    'MySQL': ['mysql'], 'Git': ['git'], 'Docker': ['docker'],
    'FastAPI': ['fastapi'], 'Flask': ['flask'], 'Django': ['django'],
    'C++': ['c++'], 'C#': ['c#'], '.NET': ['.net', 'dotnet'],
    'REST API': ['rest api', 'rest apis', 'restful api', 'restful apis'],
    'Machine learning': ['machine learning'], 'Data analysis': ['data analysis'],
    'Excel': ['excel'], 'Communication': ['communication'],
    'Teamwork': ['teamwork', 'team work'], 'Problem solving': ['problem solving', 'problem-solving'],
}


def find_skills(text: str) -> set[str]:
    text = ' '.join(text.lower().split())
    return {name for name, aliases in SKILLS.items()
            if any(re.search(r'(?<![\w+#.])' + re.escape(alias) + r'(?![\w+#])', text)
                   for alias in aliases)}


def analyze(resume: str, job: str) -> dict:
    required = find_skills(job)
    matched = sorted(required & find_skills(resume))
    missing = sorted(required - find_skills(resume))
    suggestions = []
    # Only replace a starting verb; never manufacture metrics or experience.
    for line in resume.splitlines():
        original = line.strip()
        for old, new in [('Made ', 'Created '), ('Worked on ', 'Contributed to ')]:
            if original.lower().startswith(old.lower()):
                suggestions.append({'original': original, 'revised': new + original[len(old):],
                                    'reason': 'A simple wording alternative. Review it for accuracy.'})
                break
        if len(suggestions) == 5:
            break
    return {'score': round(len(matched) / len(required) * 100) if required else None,
            'matched': matched, 'missing': missing, 'total': len(required),
            'suggestions': suggestions, 'mode': 'rule-based'}
