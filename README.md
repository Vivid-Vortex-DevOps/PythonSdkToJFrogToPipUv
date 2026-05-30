# PythonSdkToJFrogToPipUv

POC: build a Python package, publish it to **JFrog Artifactory (PyPI repo)** via GitHub Actions, and install it with `pip` or `uv`.

---

## Project structure

```
PythonSdkToJFrogToPipUv/
├── hello_sdk/               ← the Python package
│   ├── __init__.py
│   └── hello.py             greet() + main()
├── pyproject.toml           modern build config (setuptools + wheel)
├── docker-compose.yml       JFrog Artifactory OSS via Docker
├── scripts/
│   └── setup_jfrog_local.py auto-creates the PyPI repo via REST API
├── .github/workflows/
│   └── publish.yml          GitHub Actions: build → publish to JFrog
├── .env.example             secrets template
└── .gitignore
```

---

## Local workflow (Docker Desktop)

```powershell
# 1. Start Artifactory (first boot takes ~90s)
docker compose up -d

# 2. Auto-configure — creates the 'pypi-local' repo
pip install requests
python scripts/setup_jfrog_local.py

# 3. Build and publish locally
pip install build twine
python -m build
twine upload --repository-url http://localhost:8082/artifactory/api/pypi/pypi-local/ `
             -u admin -p password dist/*

# 4. Install via pip or uv
pip install hello-sdk `
  --index-url http://localhost:8082/artifactory/api/pypi/pypi-local/simple/ `
  --trusted-host localhost

uv add hello-sdk --index-url http://localhost:8082/artifactory/api/pypi/pypi-local/simple/
```

Artifactory UI: **http://localhost:8082/ui** (admin / password)

---

## GitHub Actions workflow

The workflow (`.github/workflows/publish.yml`) triggers on `v*.*.*` tags or manually via the Actions tab.

You need three **GitHub secrets** set on the repository:

| Secret | Example value |
|---|---|
| `JFROG_PYPI_URL` | `https://mycompany.jfrog.io/artifactory/api/pypi/pypi-local/` |
| `JFROG_USERNAME` | `admin` (or your JFrog Cloud user) |
| `JFROG_PASSWORD` | your password / API key |

To trigger a release:

```bash
git tag v0.1.0
git push --tags
```

---

## About the JFrog repo type

**JFrog Artifactory PyPI** is the right term — it is a **local PyPI repository** inside Artifactory (not npm, Maven, etc.). The upload endpoint is used by `twine` pointing at `/artifactory/api/pypi/<repo-name>/`, and `pip`/`uv` consume the `/simple/` index URL from that same repo.
