# MLOps Demo

A small house-price prediction service for learning the practical MLOps path
from a model to an API, tests, Docker images, Compose services, and a webhook.
The model is intentionally simple so the focus stays on packaging, deployment,
and operational workflow.

The full teaching walkthrough is in
[the course guide](readme/MLOps_course_material_By_Mehdi_Docker_Part01.md).

## Contents

- [What the project does](#what-the-project-does)
- [Project files](#project-files)
- [Prerequisites](#prerequisites)
- [Step-by-step quick start](#step-by-step-quick-start)
- [Run and test locally](#run-and-test-locally)
- [Use the API](#use-the-api)
- [Run with Docker Compose](#run-with-docker-compose)
- [Install the CrewAI skill in VS Code](#install-the-crewai-skill-in-vs-code)
- [Push a feature branch to GitHub](#push-a-feature-branch-to-github)

## What the project does

The FastAPI service fits a scikit-learn linear regression model when the app
starts. It uses five synthetic examples that map room count to price, so a
request for three rooms predicts approximately `300` model units. The service
provides:

| Route | Purpose |
| --- | --- |
| `GET /health` | Return service status and configured app version. |
| `GET /model/info` | Return model type, feature, target, coefficient, and intercept. |
| `POST /predict` | Validate a positive room count and return a price prediction. |

When `WEBHOOK_URL` is set, a prediction schedules a best-effort HTTP POST with
the input and prediction as a background task. Webhook errors are logged and do
not change the prediction response. This in-process background task is not a
durable queue and does not retry delivery after a process failure.

## Project files

```text
app/                    FastAPI app, configuration, model, schemas, webhook
tests/                  In-process API tests
scripts/                Docker preflight, smoke test, optional Flask receiver
readme/                 Full teaching walkthrough
requirements.txt        Pinned pip dependencies
pyproject.toml           Poetry project and dependency configuration
Dockerfile.fastapi       Pip-based container build
Dockerfile.poetry        Multi-stage Poetry-based container build
docker-compose.yml       API and httpbin webhook receiver services
.dockerignore            Files excluded from Docker build context
.gitignore               Generated and local-only files excluded from Git
```

## Prerequisites

- Python 3.11 or newer for local development
- Docker Desktop with Docker Compose v2 for container workflows
- Git for version control
- Node.js LTS only if installing the optional CrewAI skill below

### Windows setup

Install Git for Windows from the official
[Git for Windows page](https://git-scm.com/install/windows). Open a new
PowerShell window and verify it:

```powershell
git --version
```

For example, successful output may look like:

```text
git version 2.40.0.windows.1
```

Configure the name and email Git should record in your commits. Replace the
examples with your own details:

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Check the values with `git config --global --list`.

Install Python 3.11 or newer from the official Python distribution or use the
Python launcher if it is already installed.

### Docker Desktop with WSL 2

For this Linux-container project, Docker Desktop's WSL 2 backend is recommended
for most Windows users. Review Docker's current
[Windows installation requirements](https://docs.docker.com/desktop/setup/install/windows-install/)
before installing.

In an Administrator PowerShell window, install or update WSL 2, then restart
Windows if prompted:

```powershell
wsl --install
wsl --update
wsl --version
```

Set WSL 2 as the default version for newly installed Linux distributions:

```powershell
wsl --set-default-version 2
```

Docker Desktop currently requires WSL 2.1.5 or later for the WSL backend. If
needed, follow Microsoft's [WSL installation guide](https://learn.microsoft.com/windows/wsl/install).
Install Docker Desktop from the linked Docker page and select **Use WSL 2
instead of Hyper-V** in the installer. After Docker Desktop starts, open
**Settings > Resources > WSL Integration**, enable the Ubuntu distribution you
use, and select **Apply & restart**.

WSL 2 runs a Linux kernel and provides Bash/Linux tools, which makes the
container workflow more like Linux-based servers and CI. It is also the
recommended place to run this project's Bash smoke test. For intensive file
work inside WSL, keeping the project under the Linux home directory (such as
`~/projects`) can avoid slower cross-filesystem operations through `/mnt/c/`.

Verify the Docker engine and Compose from PowerShell or the integrated WSL
terminal:

```powershell
docker --version
docker compose version
docker run hello-world
```

The optional `uv` Python package manager can be installed in PowerShell with:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Open a new PowerShell window, then verify the installation:

```powershell
uv --version
```

## Step-by-step quick start

This is the fastest path from a fresh clone to a working prediction. The
model trains automatically when the FastAPI app starts.

### 1. Create and activate a virtual environment

From the project root:

``````Anaconda Prompt (Conda env)
cd C:\....\mlops_project01_revised

conda create -n mlops python=3.11 -y
conda activate mlops
conda deactivate

```

### 2. Install the dependencies

```Anaconda Prompt
python -m pip install -r requirements.txt
```

### 3. Run the tests

```Anaconda Prompt
pytest -q
pytest --collect-only

```

also 
```Anaconda Prompt
python -m pytest -q

```

#### How it works : 
Pytest searches the current directory and subdirectories for test files with names such as: test_api.py . 

#### Note : 
pytest -q
================================================= test session starts =================================================
platform win32 -- Python 3.11.16, pytest-8.3.3, pluggy-1.6.0
rootdir: C:\Docs\Mehdi\Teaching\MLOps\python_code\mlops_project01_revised
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.15.1
collected 8 items

tests\test_api.py ........                                                                                       [100%]

================================================== warnings summary ===================================================
..\..\..\..\..\..\Users\zadeh\.conda\envs\mlops\Lib\site-packages\starlette\testclient.py:40
  C:\Users\zadeh\.conda\envs\mlops\Lib\site-packages\starlette\testclient.py:40: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

..\..\..\..\..\..\Users\zadeh\.conda\envs\mlops\Lib\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\zadeh\.conda\envs\mlops\Lib\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_version" in PredictResponse has conflict with protected namespace "model_".

  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

..\..\..\..\..\..\Users\zadeh\.conda\envs\mlops\Lib\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\zadeh\.conda\envs\mlops\Lib\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_version" in WebhookPayload has conflict with protected namespace "model_".

  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================================ 8 passed, 3 warnings in 3.71s ============================================



### 4. Start the FastAPI server

```Anaconda Prompt
uvicorn app.main:app --reload
```

The server is now running at `http://localhost:8000`.

http://127.0.0.1:8000/docs

### 5. Make a prediction

In a new terminal (with the same virtual environment activated):

```powershell
.\.venv\Scripts\Activate.ps1
Invoke-RestMethod -Uri http://localhost:8000/predict `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"rooms": 3}'
```

``` Anaconda Prompt (Recommended)
curl -X POST http://localhost:8000/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"rooms\": 3}"
    -Body '{"rooms": 3}'


curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"rooms\": 3}"

```

Expected response:

```json
{
    "rooms": 3,
    "predicted_price": 300.0
}
```

### 6. Stop the server

Press `Ctrl+C` in the terminal running uvicorn.

---

## Run and test locally

From the project root, create and activate a Python 3.11 virtual environment,
install the pinned dependencies, and run the tests:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
pytest -q
```

Start the development server:

```powershell
uvicorn app.main:app --reload
```

Stop the server with `Ctrl+C`. The interactive API documentation is at
`http://localhost:8000/docs` and the OpenAPI schema is at
`http://localhost:8000/openapi.json`.

## Use the API

PowerShell health and metadata checks:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/model/info
```

Submit a prediction:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/predict `
	-Method Post `
	-ContentType "application/json" `
	-Body '{"rooms": 3}'
```

The `rooms` value must be greater than zero. Invalid or missing values receive
HTTP `422` from FastAPI validation.

## Run with Docker Compose 

From the project root, check that Docker Desktop, Compose, and the engine are
available:

```powershell
cd C:\....\mlops_project01_revised

Get-ChildItem .\scripts\



Directory: C:\Docs\Mehdi\Teaching\MLOps\python_code\mlops_project01_revised\scripts


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----        2026-10-01   1:11 PM           2852 check_docker.ps1
-a----        2026-10-01   1:11 PM           2980 smoke_test.sh
-a----        2026-10-01   1:11 PM           1140 webhook_receiver.py





```

If PowerShell reports that script execution is disabled, allow scripts for only your user account:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```


The check exits with an error if Docker is missing from `PATH`, Compose v2 is
unavailable, or the Docker Engine is not running. Start Docker Desktop and run
the check again if the engine cannot be reached.

```powershell
docker --version
docker info 
```

Build and start the stack from the project root:

```powershell
docker compose up --build
```
It is equal to

```powershell
docker build -f Dockerfile.fastapi -t ml-api:dev .
docker run -p 8000:8000 ...

docker pull kennethreitz/httpbin
docker run -p 8080:80 kennethreitz/httpbin

```
Note : 
https://hub.docker.com/r/kennethreitz/httpbin


kennethreitz/httpbin is a small HTTP request-and-response testing service. It does not provide a business API or store application data. Instead, it gives predictable endpoints for testing HTTP clients, proxies, webhooks, headers, authentication, delays, and error handling.




The API is exposed at `http://localhost:8000`; httpbin is exposed at
`http://localhost:8080`. Within the Compose network, the API calls
`http://webhook-receiver/anything/notify`: containers use the service DNS name
and the receiver's internal port `80`, not the host-mapped port `8080`.
httpbin echoes received requests; it does not provide a persistent history.

Useful Compose commands:

```powershell
docker compose ps
docker compose logs -f ml-api
docker compose down
```

The end-to-end `scripts/smoke_test.sh` is a Bash script. Run it from WSL or Git
Bash, from the project root, after starting the Compose stack. It checks the
API routes, response fields, validation status, receiver reachability, and a
new webhook success entry in the API container logs:

```bash
./scripts/smoke_test.sh
```

### Choose the Poetry Dockerfile

The default Compose configuration builds with `Dockerfile.fastapi`. To use the
multi-stage Poetry build instead, change the `ml-api.build.dockerfile` value in
`docker-compose.yml` to `Dockerfile.poetry`. Generate `poetry.lock` first:

```powershell
python -m pip install poetry
poetry lock
docker compose up --build
```

The Poetry Dockerfile exports only the main/runtime dependency group into its
final image. The pip Dockerfile installs from `requirements.txt`.

## Install the CrewAI skill in VS Code

The skill installer requires Node.js, which includes npm and npx. Install the
current LTS version from the official
[Node.js download page](https://nodejs.org/en/download), then open a new
PowerShell window and verify the tools:

```powershell
node --version
npm --version
npx.cmd --version
```

From the project root, install the CrewAI skills:

```powershell
npx.cmd skills add crewaiinc/skills
```

If PowerShell blocks the installer, you may set the execution policy for your
current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

`RemoteSigned` is not unrestricted permission: local scripts may run, while
downloaded scripts must be signed. Review third-party skill files before use
and reload VS Code after installation so it can discover the skills.

## Push a feature branch to GitHub

Confirm the GitHub repository is configured as `origin`:

```powershell
git remote -v
```

If `origin` is missing, add the repository URL provided by your instructor or
organization:

```powershell
git remote add origin https://github.com/OWNER/REPOSITORY.git
```

Create and switch to the requested branch. This command is for creating the
branch the first time; if it already exists locally, use
`git switch feature/mlops_01` instead:

```powershell
git switch -c feature/mlops_01
```

If the branch exists on GitHub but not on your computer, fetch it and create a
local branch that tracks it:

```powershell
git fetch origin
git switch --track origin/feature/mlops_01
```

Review the changes before staging, and do not include secrets, virtual
environments, or other local-only files:

```powershell
git status
git add -A
git status
git commit -m "Add MLOps demo project"
git push -u origin feature/mlops_01
```

Git Credential Manager may open a browser for GitHub sign-in during the push.
Authenticate in the browser; GitHub account passwords are not used directly for
HTTPS Git operations. Never paste passwords, access tokens, or other secrets
into chat or commit them to the repository.