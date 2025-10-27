# 🧠 pyteam-skills

Generate a **team skill matrix** and interactive **dashboard** from your Git commit history.  
It mines repositories with [PyDriller], maps files to skills (via extensions, paths, or regex), applies configurable weights with **recency decay**, and produces both **CSV exports** and a modern **Tailwind dashboard** (with dark mode + filters).

![Dashboard Screenshot](https://github.com/hassanzaib512/pyteam-skills/blob/main/examples/example.png?raw=1)

---

## 🚀 Features

- 🪄 **Git mining** via [PyDriller]
- 🧩 **Skill mapping precedence:** `regex → path prefix → extension → Other`
- ⚖️ **Weighted scoring** — with configurable parameters and **exponential recency decay**
- 📊 **Normalized skill matrix (1–100)** — top contributor per skill = 100
- 📈 **Monthly trends** — per skill, normalized (1–100)
- 🌗 **Static dashboard** — filters by Author, Skill, Month + dark mode + download JSON
- 🧰 **CLI-powered workflow:** `init`, `scan`, `matrix`, `dashboard`
- 🚧 **More features coming soon!**

---

## 🛠️ Installation (Development Mode)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

For normal installation:

```bash
pip install pyteam-skills
```

---

## ⚡ Quickstart

```bash
# 1) Create a default configuration
pyteam-skills init --out config.yml

# 2) Scan a Git repository
pyteam-skills scan --repo . --config config.yml --out artifacts/scan.json

# 3) Export CSV artifacts
pyteam-skills matrix --scan artifacts/scan.json --out artifacts

# 4) Generate the interactive dashboard
pyteam-skills dashboard --scan artifacts/scan.json --out artifacts/dashboard

# 5) Open your dashboard in a browser
open artifacts/dashboard/index.html
```

---

## ⚙️ Config Reference

See [`examples/config.example.yml`](https://github.com/hassanzaib512/pyteam-skills/blob/main/examples/config.example.yml?raw=1).

### Skill Mapping Precedence

1. **regex_skills** (first match wins)  
2. **path_skills** (longest prefix wins)  
3. **extension_skills**  
4. fallback → `["Other"]`

### Weight Parameters

| Parameter | Description | Default |
|------------|-------------|----------|
| `lines_changed` | Weight for added + deleted lines | `1.0` |
| `files_touched` | Weight per file touched | `0.3` |
| `commit_bonus` | Constant bonus per commit | `0.2` |
| `decay_half_life_days` | Half-life for exponential recency decay | `120` |

---

## 🧪 Development

```bash
make format   # Format code with black
make lint     # Run ruff linter
make test     # Run pytest
make all      # Format + lint + test
```

---

## 📜 License

MIT License © [Hassan Zaib Hayat](https://github.com/hassanzaib512)

---

[PyDriller]: https://github.com/ishepard/pydriller
