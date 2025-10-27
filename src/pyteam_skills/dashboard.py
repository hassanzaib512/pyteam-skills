"""Static dashboard generator (single-file HTML with embedded JSON)."""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json
import os

from .matrix import build_skill_matrix, _normalize_matrix, build_trends


def _to_serializable(df):
    """Convert pandas DataFrame to a JSON-serializable dict."""
    return {
        "index": list(df.index),
        "columns": list(df.columns),
        "data": [[float(x) for x in row] for row in df.to_numpy()],
    }


def _make_html() -> str:
    """Return the static dashboard HTML (triple-quoted to avoid syntax issues)."""
    return """<!doctype html>
<html lang="en" class="h-full">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Skills Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config={darkMode:'class',theme:{extend:{fontFamily:{sans:['Inter','ui-sans-serif','system-ui']},boxShadow:{'xl-soft':'0 10px 25px -5px rgba(0,0,0,.08), 0 8px 10px -6px rgba(0,0,0,.06)'}}}};</script>
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    .chip{display:inline-flex;align-items:center;border-radius:9999px;padding:.25rem .625rem;font-size:.75rem;font-weight:500;background:#f1f5f9;color:#334155}
    .dark .chip{background:#0f172a;color:#e2e8f0}
    .btn { display:inline-flex; align-items:center; gap:.5rem; border-radius:0.75rem; padding:.5rem 1rem; font-weight:600; }
    .btn-primary { background:#4f46e5; color:white; box-shadow:0 8px 20px -6px rgba(79,70,229,.45); }
    .btn-primary:hover { background:#6366f1; }
    .btn-ghost { background:rgba(99,102,241,.12); color:#c7d2fe; }
    .btn-ghost:hover { background:rgba(99,102,241,.2); }
    .btn-soft { background:#eef2ff; color:#3730a3; border:1px solid #e5e7eb; }
    .btn-soft:hover { background:#e0e7ff; }
    .dark .btn-soft { background:#0f172a; color:#e0e7ff; border-color:#334155; }
    .dark .btn-soft:hover { background:#1f2937; }
    .select-wrap { position:relative; }
    .select { appearance:none; width:100%; border-radius:0.75rem; padding:.5rem .75rem; padding-right:2.25rem;
              border:1px solid var(--twc-border, #e5e7eb); background:var(--twc-bg, #fff); }
    .dark .select { --twc-border:#334155; --twc-bg:#0f172a; color:#e2e8f0; }
    .select:focus { outline:2px solid transparent; outline-offset:2px; box-shadow:0 0 0 3px rgba(99,102,241,.35); }
    .select-chevron { position:absolute; right:.625rem; top:50%; transform:translateY(-50%); pointer-events:none; opacity:.7; }
    .select-sm { padding:.375rem .625rem; padding-right:2rem; font-size:.875rem; }
    .input-sm { padding:.375rem .625rem; font-size:.875rem; border:1px solid var(--twc-border, #e5e7eb); background:var(--twc-bg, #fff); border-radius:0.75rem; }
    .dark .input-sm { --twc-border:#334155; --twc-bg:#0f172a; color:#e2e8f0; }
  </style>
</head>
<body class="h-full bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
  <div class="sticky top-0 z-20 backdrop-blur bg-white/70 dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-800">
    <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="h-8 w-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600"></div>
        <h1 class="text-lg font-semibold">Skills Dashboard</h1>
      </div>
      <div class="flex items-center gap-3">
        <button id="darkToggle" class="btn btn-soft">🌙 Theme</button>
        <a id="downloadJson" class="btn btn-soft" download="data.json">⬇️ Download Data</a>
      </div>
    </div>
  </div>

  <main class="max-w-7xl mx-auto px-4 py-8 space-y-8">
    <!-- Filters -->
    <section class="rounded-2xl p-6 bg-white dark:bg-slate-900 shadow-xl-soft border border-slate-100 dark:border-slate-800">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
        <div class="flex-1">
          <label class="block text-sm text-slate-600 dark:text-slate-300 mb-1">Author</label>
          <div class="select-wrap">
            <select id="authorSelect" class="select select-sm"><option value="">All Authors</option></select>
            <svg class="select-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
          </div>
        </div>
        <div class="flex-1">
          <label class="block text-sm text-slate-600 dark:text-slate-300 mb-1">Skill</label>
          <div class="select-wrap">
            <select id="skillSelect" class="select select-sm"><option value="">All Skills</option></select>
            <svg class="select-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
          </div>
        </div>
        <div class="flex-1">
          <label class="block text-sm text-slate-600 dark:text-slate-300 mb-1">Month</label>
          <div class="select-wrap">
            <select id="monthSelect" class="select select-sm"><option value="">All Months</option></select>
            <svg class="select-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
          </div>
        </div>
        <div class="flex-1">
          <label class="block text-sm text-slate-600 dark:text-slate-300 mb-1">Search</label>
          <input id="searchInput" placeholder="Search author or skill..." class="w-full input-sm"/>
        </div>
        <div class="flex md:justify-end">
          <button id="resetBtn" class="btn btn-primary w-full md:w-auto">↻ Reset</button>
        </div>
      </div>
      <div id="activeChips" class="mt-4 flex flex-wrap gap-2"></div>
    </section>

    <!-- KPIs -->
    <section class="grid md:grid-cols-4 gap-4">
      <div class="rounded-2xl p-5 bg-white dark:bg-slate-900 shadow-xl-soft border border-slate-100 dark:border-slate-800"><div class="text-sm text-slate-500">Total Authors</div><div id="kpiAuthors" class="text-3xl font-semibold mt-1">–</div></div>
      <div class="rounded-2xl p-5 bg-white dark:bg-slate-900 shadow-xl-soft border border-slate-100 dark:border-slate-800"><div class="text-sm text-slate-500">Total Skills</div><div id="kpiSkills" class="text-3xl font-semibold mt-1">–</div></div>
      <div class="rounded-2xl p-5 bg-white dark:bg-slate-900 shadow-xl-soft border border-slate-100 dark:border-slate-800"><div class="text-sm text-slate-500">Top Skill (sum of norm)</div><div id="kpiTopSkill" class="text-xl font-semibold mt-1">–</div></div>
      <div class="rounded-2xl p-5 bg-white dark:bg-slate-900 shadow-xl-soft border border-slate-100 dark:border-slate-800">
        <div class="text-sm text-slate-500">Busiest Author</div>
        <div class="mt-1 space-y-0.5">
          <div id="kpiTopAuthorName" class="text-base font-semibold whitespace-normal break-words">—</div>
          <div id="kpiTopAuthorEmail" class="text-xs text-slate-500 whitespace-normal break-words">—</div>
        </div>
      </div>
    </section>

    <!-- Matrix -->
    <section class="rounded-2xl p-6 bg-white dark:bg-slate-900 shadow-xl-soft border border-slate-100 dark:border-slate-800">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">Skill Matrix <span class="text-slate-500">(normalized 1–100)</span></h2>
        <div class="text-xs text-slate-500">Top contributor per skill = 100</div>
      </div>
      <div class="overflow-auto rounded-xl border border-slate-200 dark:border-slate-800">
        <table class="w-full text-sm" id="matrixTable">
          <thead class="bg-slate-50 dark:bg-slate-800"></thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800"></tbody>
        </table>
      </div>
      <!-- Matrix pagination controls -->
      <div class="flex items-center justify-between mt-3 text-sm">
        <div class="flex items-center gap-2">
          <label class="text-slate-600 dark:text-slate-300">Rows per page</label>
          <select id="matrixPageSize" class="select select-sm" style="width:auto">
            <option>10</option>
            <option selected>20</option>
            <option>50</option>
            <option>100</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <button id="matrixPrev" class="btn btn-soft">&larr; Prev</button>
          <span id="matrixPageInfo" class="text-slate-500"></span>
          <button id="matrixNext" class="btn btn-soft">Next &rarr;</button>
        </div>
      </div>
    </section>

    <!-- Trends -->
    <section class="rounded-2xl p-6 bg-white dark:bg-slate-900 shadow-xl-soft border border-slate-100 dark:border-slate-800">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">Monthly Trends <span class="text-slate-500">(normalized 1–100)</span></h2>
        <div class="text-xs text-slate-500">Per (month, skill), top author = 100</div>
      </div>
      <div class="overflow-auto rounded-xl border border-slate-200 dark:border-slate-800">
        <table class="w-full text-sm" id="trendTable">
          <thead class="bg-slate-50 dark:bg-slate-800">
            <tr><th class="px-4 py-3 text-left">Month</th><th class="px-4 py-3 text-left">Skill</th><th class="px-4 py-3 text-left">Author</th><th class="px-4 py-3 text-left">Score</th></tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800"></tbody>
        </table>
      </div>
      <!-- Trends pagination controls -->
      <div class="flex items-center justify-between mt-3 text-sm">
        <div class="flex items-center gap-2">
          <label class="text-slate-600 dark:text-slate-300">Rows per page</label>
          <select id="trendPageSize" class="select select-sm" style="width:auto">
            <option>10</option>
            <option selected>25</option>
            <option>50</option>
            <option>100</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <button id="trendPrev" class="btn btn-soft">&larr; Prev</button>
          <span id="trendPageInfo" class="text-slate-500"></span>
          <button id="trendNext" class="btn btn-soft">Next &rarr;</button>
        </div>
      </div>
    </section>
  </main>

  <!-- Keep this placeholder BEFORE the main script so it's available when parsed.
       The generator will inject JSON into ALL placeholders with this exact markup. -->
  <script id="data-script" type="application/json"></script>

  <script>
    // Load embedded data (first placeholder already has data after generation)
    const DATA = JSON.parse(document.getElementById('data-script').textContent);

    // Pagination state & helpers
    const matrixState = { page: 0, size: 20 };
    const trendState  = { page: 0, size: 25 };
    function clamp(v, min, max){ return Math.max(min, Math.min(max, v)); }
    function paginate(arr, page, size){
      const totalPages = Math.max(1, Math.ceil(arr.length / size));
      const p = clamp(page, 0, totalPages - 1);
      const start = p * size, end = start + size;
      return { slice: arr.slice(start, end), page: p, totalPages };
    }

    const authorSelect=document.getElementById('authorSelect'),
          skillSelect=document.getElementById('skillSelect'),
          monthSelect=document.getElementById('monthSelect'),
          searchInput=document.getElementById('searchInput'),
          resetBtn=document.getElementById('resetBtn'),
          activeChips=document.getElementById('activeChips'),
          downloadJson=document.getElementById('downloadJson');

    const darkToggle=document.getElementById('darkToggle'), root=document.documentElement;
    function applyDark(saved){ if(saved==='dark') root.classList.add('dark'); else root.classList.remove('dark'); }
    const savedTheme=localStorage.getItem('pyteam-dark')||(window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'); applyDark(savedTheme); syncToggleUI();
    function syncToggleUI(){
      const isDark = root.classList.contains('dark');
      darkToggle.setAttribute('aria-pressed', String(isDark));
      darkToggle.textContent = isDark ? '☀️ Light' : '🌙 Dark';
    }
    darkToggle.addEventListener('click', ()=>{
      const next = root.classList.contains('dark') ? 'light' : 'dark';
      localStorage.setItem('pyteam-dark', next);
      applyDark(next);
      syncToggleUI();
    });

    const authors=DATA.matrix_norm.index, skills=DATA.matrix_norm.columns;
    authors.forEach(a=>{const o=document.createElement('option');o.value=a;o.textContent=a;authorSelect.appendChild(o);});
    skills.forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=s;skillSelect.appendChild(o);});
    const monthsSet = new Set((DATA.trends||[]).map(r=>r.month));
    Array.from(monthsSet).sort().forEach(m=>{const o=document.createElement('option');o.value=m;o.textContent=m;monthSelect.appendChild(o);});

    const blob=new Blob([JSON.stringify(DATA)],{type:'application/json'}); downloadJson.href=URL.createObjectURL(blob);

    function renderChips(){ activeChips.innerHTML=''; const chips=[];
      if(authorSelect.value) chips.push({label:`Author: ${authorSelect.value}`,clear:()=>authorSelect.value=''});
      if(skillSelect.value) chips.push({label:`Skill: ${skillSelect.value}`,clear:()=>skillSelect.value=''});
      if(monthSelect.value) chips.push({label:`Month: ${monthSelect.value}`,clear:()=>monthSelect.value=''});
      if(searchInput.value) chips.push({label:`Search: ${searchInput.value}`,clear:()=>searchInput.value=''});
      chips.forEach(c=>{ const s=document.createElement('span'); s.className='chip'; s.innerHTML=`${c.label} <button class="ml-2">✕</button>`; s.querySelector('button').addEventListener('click',()=>{c.clear(); rerender();}); activeChips.appendChild(s); });
    }

    function computeKPIs(){
      const raw=DATA.matrix_raw, norm=DATA.matrix_norm;
      const totalAuthors=raw.index.length, totalSkills=raw.columns.length;
      let topSkill=null, topSkillSum=-1;
      for(let j=0;j<norm.columns.length;j++){ let sum=0; for(let i=0;i<norm.index.length;i++) sum+=norm.data[i][j]; if(sum>topSkillSum){topSkillSum=sum; topSkill=norm.columns[j];}}
      let topAuthor=null, topAuthorSum=-1;
      for(let i=0;i<raw.index.length;i++){ let sum=raw.data[i].reduce((a,b)=>a+b,0); if(sum>topAuthorSum){topAuthorSum=sum; topAuthor=raw.index[i];}}
      document.getElementById('kpiAuthors').textContent=totalAuthors; document.getElementById('kpiSkills').textContent=totalSkills; document.getElementById('kpiTopSkill').textContent=topSkill||'—';
      (function(){
        const top = topAuthor || '—';
        let name = top, email = '';
        const m = top && top.match(/^(.*)\s*<([^>]+)>/);
        if (m) { name = (m[1]||'—').trim(); email = (m[2]||'').trim(); }
        const nameEl = document.getElementById('kpiTopAuthorName');
        const emailEl = document.getElementById('kpiTopAuthorEmail');
        if (nameEl) { nameEl.textContent = name; nameEl.title = top; }
        if (emailEl) { emailEl.textContent = email; emailEl.title = top; }
      })();
    }

    // MATRIX (rows = authors) with pagination
    const matrixTable=document.getElementById('matrixTable');
    function renderMatrix(){
      const skillFilter=skillSelect.value, authorFilter=authorSelect.value, q=searchInput.value.toLowerCase();

      // Filter rows (authors)
      let rowsIdx=[...DATA.matrix_norm.index];
      if(authorFilter) rowsIdx=rowsIdx.filter(a=>a===authorFilter);
      if(q) rowsIdx=rowsIdx.filter(a=>a.toLowerCase().includes(q));

      // Paginate rows
      const { slice, page, totalPages } = paginate(rowsIdx, matrixState.page, matrixState.size);
      matrixState.page = page;

      // Columns (skills)
      let cols=[...DATA.matrix_norm.columns];
      if(skillFilter) cols=cols.filter(c=>c===skillFilter);
      if(q && !authorFilter) cols=cols.filter(c=>c.toLowerCase().includes(q) || rowsIdx.length>0);
      const colIndices=cols.map(c=>DATA.matrix_norm.columns.indexOf(c));

      // Render table
      const thead=matrixTable.querySelector('thead'), tbody=matrixTable.querySelector('tbody'); thead.innerHTML=''; tbody.innerHTML='';
      const headRow=document.createElement('tr');
      headRow.innerHTML=`<th class="px-4 py-3 text-left">Author</th>`+cols.map(c=>`<th class="px-4 py-3 text-left">${c}</th>`).join('');
      thead.appendChild(headRow);

      for(const a of slice){
        const i=DATA.matrix_norm.index.indexOf(a);
        const tr=document.createElement('tr'); tr.className='hover:bg-slate-50/60 dark:hover:bg-slate-800/50';
        let cells=`<td class="px-4 py-3 font-medium whitespace-nowrap">${a}</td>`;
        for(const j of colIndices){
          const val=Math.round(DATA.matrix_norm.data[i][j]||0);
          cells+=`<td class="px-4 py-3"><div class="h-2 rounded bg-slate-200 dark:bg-slate-800"><div class="h-2 rounded bg-gradient-to-r from-indigo-500 to-violet-600" style="width:${Math.max(0,Math.min(100,val))}%"></div></div><div class="text-xs text-slate-500 mt-1">${val}</div></td>`;
        }
        tr.innerHTML=cells; tbody.appendChild(tr);
      }

      // Update pagination UI
      const info = document.getElementById('matrixPageInfo');
      if (info) info.textContent = `Page ${page+1} of ${Math.max(1,Math.ceil(rowsIdx.length/matrixState.size))}`;
      const prev = document.getElementById('matrixPrev');
      const next = document.getElementById('matrixNext');
      if(prev) prev.disabled = page <= 0;
      if(next) next.disabled = (page+1) >= Math.max(1,Math.ceil(rowsIdx.length/matrixState.size));
    }

    // TRENDS with pagination
    const trendTable=document.getElementById('trendTable');
    function renderTrends(){
      const skillFilter=skillSelect.value, authorFilter=authorSelect.value, monthFilter=monthSelect.value, q=searchInput.value.toLowerCase();
      const filtered=(DATA.trends||[])
        .filter(r=>!skillFilter||r.skill===skillFilter)
        .filter(r=>!authorFilter||r.author===authorFilter)
        .filter(r=>!monthFilter||r.month===monthFilter)
        .filter(r=>r.author.toLowerCase().includes(q)||r.skill.toLowerCase().includes(q)||r.month.includes(q));

      const { slice, page, totalPages } = paginate(filtered, trendState.page, trendState.size);
      trendState.page = page;

      const tbody=trendTable.querySelector('tbody'); tbody.innerHTML='';
      slice.forEach(r=>{
        const tr=document.createElement('tr'); tr.className='hover:bg-slate-50/60 dark:hover:bg-slate-800/50';
        tr.innerHTML=`<td class="px-4 py-3">${r.month}</td><td class="px-4 py-3">${r.skill}</td><td class="px-4 py-3 whitespace-nowrap">${r.author}</td><td class="px-4 py-3">${r.norm}</td>`;
        tbody.appendChild(tr);
      });

      const info = document.getElementById('trendPageInfo');
      if (info) info.textContent = `Page ${page+1} of ${totalPages}`;
      const prev = document.getElementById('trendPrev');
      const next = document.getElementById('trendNext');
      if(prev) prev.disabled = page <= 0;
      if(next) next.disabled = page >= totalPages-1;
    }

    // Controls wiring
    const matrixPrev = document.getElementById('matrixPrev');
    const matrixNext = document.getElementById('matrixNext');
    const matrixPageSize = document.getElementById('matrixPageSize');
    if(matrixPrev) matrixPrev.addEventListener('click', () => { matrixState.page = Math.max(0, matrixState.page - 1); renderMatrix(); });
    if(matrixNext) matrixNext.addEventListener('click', () => { matrixState.page = matrixState.page + 1; renderMatrix(); });
    if(matrixPageSize) matrixPageSize.addEventListener('change', (e) => { matrixState.size = parseInt(e.target.value, 10)||20; matrixState.page = 0; renderMatrix(); });

    const trendPrev = document.getElementById('trendPrev');
    const trendNext = document.getElementById('trendNext');
    const trendPageSize = document.getElementById('trendPageSize');
    if(trendPrev) trendPrev.addEventListener('click', () => { trendState.page = Math.max(0, trendState.page - 1); renderTrends(); });
    if(trendNext) trendNext.addEventListener('click', () => { trendState.page = trendState.page + 1; renderTrends(); });
    if(trendPageSize) trendPageSize.addEventListener('change', (e) => { trendState.size = parseInt(e.target.value, 10)||25; trendState.page = 0; renderTrends(); });

    // Reset pages when filters/search change
    function rerender(){
      matrixState.page = 0; trendState.page = 0;
      renderChips(); computeKPIs(); renderMatrix(); renderTrends();
    }
    authorSelect.addEventListener('change', rerender);
    skillSelect.addEventListener('change', rerender);
    monthSelect.addEventListener('change', rerender);
    searchInput.addEventListener('input', rerender);
    resetBtn.addEventListener('click', ()=>{authorSelect.value=''; skillSelect.value=''; monthSelect.value=''; searchInput.value=''; rerender();});

    // Initial render
    rerender();
  </script>

  <!-- A second placeholder is kept for compatibility with the generator's replacement,
       but it's not used by the script above. -->
  <script id="data-script" type="application/json"></script>
</body>
</html>"""


def generate_dashboard(scan: Dict[str, Any], out_dir: str) -> Dict[str, str]:
    """Generate the dashboard artifacts and return their paths."""
    os.makedirs(out_dir, exist_ok=True)
    mat_raw = build_skill_matrix(scan)
    mat_norm = _normalize_matrix(mat_raw)
    trends = build_trends(scan)
    data = {
        "matrix_raw": _to_serializable(mat_raw),
        "matrix_norm": _to_serializable(mat_norm),
        "trends": trends.to_dict(orient="records"),
        "meta": {"repo": scan.get("repo"), "scanned_at": scan.get("scanned_at")},
    }
    data_path = Path(out_dir) / "data.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    html_path = Path(out_dir) / "index.html"
    page = _make_html()
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(page)

    # Embed data for single-file use (both placeholders get replaced safely)
    with open(html_path, "r+", encoding="utf-8") as f:
        content = f.read().replace(
            '<script id="data-script" type="application/json"></script>',
            '<script id="data-script" type="application/json">'
            + json.dumps(data)
            + "</script>",
        )
        f.seek(0)
        f.truncate(0)
        f.write(content)

    return {"index_html": str(html_path), "data_json": str(data_path)}
