# MLOps Demo

A small house-price prediction API used to teach FastAPI, Docker, Docker Compose,
dependency management, tests, and webhooks.

The full teaching walkthrough is in
[the course guide](readme/MLOps_course_material_By_Mehdi_Docker_Part01.md).

## Push the project on a feature branch

From the project root, create and switch to the requested branch:

```powershell
git switch -c feature/mlops_01
```

Review the files that will be included, then stage and commit the project. Make
sure no secrets or local-only files are included:

```powershell
git status
git add -A
git status
git commit -m "Add MLOps demo project"
```

Push the branch and set its upstream tracking branch. The repository must have
a remote named `origin` configured:

```powershell
git push -u origin feature/mlops_01
```

## Run locally

Requires Python 3.11 or newer.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for the API documentation.

## Install the CrewAI skill in VS Code

Install the Node.js LTS release from the official
[Node.js download page](https://nodejs.org/en/download) first. This provides
`npm` and `npx`. Open a new PowerShell window, change to this project directory,
and run:

```powershell
npx.cmd skills add crewaiinc/skills
```

If PowerShell blocks script execution, the current-user policy can be set with
the following command. `RemoteSigned` is not unrestricted permission; it allows
local scripts and requires downloaded scripts to be signed:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Review the installed third-party skill files before using them, then reload VS
Code so the skill can be discovered.

## Run with Docker Compose

```bash
docker compose up --build
```

The API is available at `http://localhost:8000`; the httpbin webhook receiver
is available at `http://localhost:8080`. The API posts notifications to
httpbin's `/anything/notify` endpoint over the Compose network. httpbin echoes
the received request; it does not provide a persistent request history.

To test the running stack from WSL or another Bash environment:

```bash
./scripts/smoke_test.sh
```

To build with the Poetry Dockerfile, first install Poetry and generate its lock
file with `poetry lock`, then use:

```bash
docker compose build --no-cache ml-api
```

Change `docker-compose.yml` from `Dockerfile.fastapi` to `Dockerfile.poetry`
when you want Compose to use the Poetry build.