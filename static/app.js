const $ = id => document.getElementById(id);
let current = null;
let accepted = new Set();
let statusTimer;
function status(message) { clearTimeout(statusTimer); $('status').textContent = message; statusTimer = setTimeout(() => $('status').textContent = '', 9000); }
async function api(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(typeof error.detail === 'string' ? error.detail : 'Check your inputs and try again.');
  }
  return response.status === 204 ? null : response.json();
}
function element(tag, text, className) {
  const node = document.createElement(tag);
  node.textContent = text;
  if (className) node.className = className;
  return node;
}
function updateRevision() {
  let text = current.resume;
  current.result.suggestions.forEach((suggestion, index) => {
    if (accepted.has(index)) text = text.replace(suggestion.original, suggestion.revised);
  });
  $('revised').value = text;
}
function show(report) {
  current = report; accepted = new Set();
  $('resume').value = report.resume; $('job').value = report.job; $('title').value = report.title;
  const result = report.result;
  $('results').hidden = false;
  $('score').textContent = result.score === null ? 'N/A' : `${result.score}%`;
  $('formula').textContent = result.total ? `${result.matched.length} matched / ${result.total} recognized job skills × 100, rounded.` : 'No skills from our dictionary were recognized in this job description.';
  $('coverage').value = result.score || 0;
  $('coverage').hidden = result.score === null;
  for (const group of ['matched', 'missing']) {
    $(group).replaceChildren(...(result[group].length ? result[group].map(skill => element('span', skill)) : [element('p', 'None identified.', 'muted')]));
  }
  $('suggestions').replaceChildren();
  result.suggestions.forEach((suggestion, index) => {
    const box = element('div', '', 'suggestion');
    box.append(element('p', `Original: ${suggestion.original}`), element('p', `Suggested: ${suggestion.revised}`), element('p', suggestion.reason, 'muted'));
    const label = element('label', ''); const check = document.createElement('input'); check.type = 'checkbox';
    check.addEventListener('change', () => { check.checked ? accepted.add(index) : accepted.delete(index); updateRevision(); });
    label.append(check, document.createTextNode('Accept this wording')); box.append(label); $('suggestions').append(box);
  });
  if (!result.suggestions.length) $('suggestions').append(element('p', 'No matching wording rules. Your text is unchanged.', 'muted'));
  updateRevision();
  $('results').scrollIntoView({behavior: 'smooth', block: 'start'});
}
async function history() {
  try {
    const reports = await api('/api/analyses'); $('history').replaceChildren();
    if (!reports.length) $('history').append(element('p', 'Your first comparison will appear here.', 'muted'));
    reports.forEach(report => {
      const row = element('div', '', 'history-item'); const open = element('button', report.title); open.type = 'button';
      open.onclick = async () => { try { show(await api(`/api/analyses/${report.id}`)); } catch (error) { status(error.message); } };
      const remove = element('button', 'Delete'); remove.type = 'button'; remove.setAttribute('aria-label', `Delete ${report.title}`);
      remove.onclick = async () => {
        try { await api(`/api/analyses/${report.id}`, {method:'DELETE'}); if (current?.id === report.id) { current = null; $('results').hidden = true; $('resume').value = ''; $('job').value = ''; $('title').value = ''; } await history(); status('Report deleted.'); } catch (error) { status(error.message); }
      };
      row.append(open, element('small', new Date(report.created_at).toLocaleString()), remove); $('history').append(row);
    });
  } catch (error) { $('history').replaceChildren(element('p', 'History could not load. Refresh to retry.', 'muted')); status(error.message); }
}
$('analysis-form').onsubmit = async event => {
  event.preventDefault(); $('analyze').disabled = true; $('analyze').textContent = 'Comparing…';
  try { show(await api('/api/analyses', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({resume:$('resume').value, job:$('job').value, title:$('title').value})})); await history(); status('Comparison saved on this computer.'); }
  catch (error) { status(error.message); }
  finally { $('analyze').disabled = false; $('analyze').textContent = 'Compare my resume'; }
};
$('pdf').onchange = async () => {
  const file = $('pdf').files[0]; if (!file) return;
  if (!file.name.toLowerCase().endsWith('.pdf') || file.size > 5 * 1024 * 1024) { status('Choose a PDF no larger than 5 MB.'); return; }
  $('pdf').disabled = true; $('analyze').disabled = true; status('Extracting PDF text…');
  try { const result = await api('/api/extract', {method:'POST', headers:{'Content-Type':'application/pdf'}, body:file}); $('resume').value = result.text; status('Text extracted. Review it before comparing.'); }
  catch (error) { status(error.message); }
  finally { $('pdf').disabled = false; $('analyze').disabled = false; $('pdf').value = ''; }
};
$('sample').onclick = () => {
  $('title').value = 'Junior Python Developer';
  $('resume').value = 'Alex Student\nComputer Science graduate\nSkills: Python, SQL, HTML, CSS, Git\nMade a student records application using Python and SQLite.\nWorked on a team project to organize college events.';
  $('job').value = 'We are hiring a junior developer with Python, SQL, Git, FastAPI and Docker skills. Experience building REST APIs is helpful.';
  status('Sample loaded. Click Compare my resume to run it.');
};
$('copy').onclick = async () => { try { await navigator.clipboard.writeText($('revised').value); status('Resume text copied.'); } catch { status('Clipboard unavailable. Select the resume text and copy it manually.'); } };
$('export').onclick = () => {
  if (!current) return;
  const result = current.result;
  const text = `${current.title}\nKeyword coverage: ${result.score === null ? 'N/A' : result.score + '%'}\nMatched: ${result.matched.join(', ')}\nNot evidenced: ${result.missing.join(', ')}\n\nRule-based comparison, not an employer ATS score.\n\nReviewed resume:\n${$('revised').value}`;
  const url = URL.createObjectURL(new Blob([text], {type:'text/plain;charset=utf-8'})); const link = element('a', ''); link.href = url; link.download = 'resume-comparison.txt'; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
};
history();

