# Mario-like 2D Game with Jenkins CI/CD, Mend, and Fortify

This repository contains:
- A Python/Pygame Mario-like game (`mario_like_game.py`)
- Docker packaging (`Dockerfile`)
- Jenkins pipeline (`Jenkinsfile`) with stages for:
  - static validation
  - Mend scan placeholder
  - Fortify scan placeholder
  - Docker build/push
  - direct Docker deployment

---

## 1) Prerequisites

## A. Accounts you need

### Mend (Yes, account required)
You need a Mend organization/account to get access token/API credentials and create a project for scans.

### Fortify (Yes, account/license required)
You need Fortify licensing/access (Fortify SAST/SSC ecosystem) to run official scans and upload results.

### Container Registry (Usually yes)
You need a registry account where Jenkins can push images (Docker Hub, ECR, ACR, GCR, Harbor, etc.).

---

## B. Jenkins server requirements
Install Jenkins on a machine that has:
- Docker engine installed and accessible by Jenkins user
- Python 3 + pip
- Git

If Jenkins itself runs in Docker, ensure Docker socket access is configured if you build images on that node.

---

## C. Jenkins plugins to install
Go to **Manage Jenkins -> Plugins** and install:
- **Pipeline**
- **Git**
- **Credentials Binding**
- **Workspace Cleanup** (optional but recommended)

For Fortify integration UI/reporting, you can also install Fortify-related Jenkins plugin(s), but CLI-based scanning works without them.

Mend can be integrated either:
- with Mend CLI in shell steps, or
- via Mend-specific Jenkins plugin (optional, depends on your org standard).

---

## 2) Project setup

1. Clone this repository.
2. Ensure these files exist:
   - `mario_like_game.py`
   - `requirements.txt`
   - `Dockerfile`
   - `Jenkinsfile`
3. Update `Jenkinsfile` placeholders:
   - `IMAGE_NAME` (your real registry/repository)
   - `DOCKER_CREDENTIALS_ID` (your Jenkins credential id)

---

## 3) Configure Jenkins credentials

Go to **Manage Jenkins -> Credentials -> (Global)** and create:

1. **Docker registry credentials**
   - Type: Username/Password
   - ID: `docker-registry-credentials` (or change Jenkinsfile to match)

2. **Mend token**
   - Type: Secret text
   - ID: `mend-token`

3. **Fortify credentials/token** (based on your Fortify setup)
   - Type: Secret text or Username/Password
   - ID example: `fortify-token`

---

## 4) Install Mend and Fortify tooling on Jenkins agent

## A. Mend CLI
Install Mend CLI on Jenkins agent machine(s), then verify:

```bash
mend --version
```

## B. Fortify tools
Install required Fortify tools (e.g., `sourceanalyzer`, and optional upload/client tooling), then verify:

```bash
sourceanalyzer -version
```

> Exact Fortify installation packages/commands depend on your licensed Fortify product edition and enterprise setup.

---

## 5) Update Jenkinsfile scan stages with real commands

Current pipeline has placeholder commands in:
- `stage('Mend Scan')`
- `stage('Fortify Scan')`

Replace placeholder scripts with your organization's actual commands.

Example shape (pseudo):

```groovy
stage('Mend Scan') {
  steps {
    withCredentials([string(credentialsId: 'mend-token', variable: 'MEND_TOKEN')]) {
      sh '''
        mend auth --token "$MEND_TOKEN"
        mend scan --project-name mario-game --path .
      '''
    }
  }
}
```

```groovy
stage('Fortify Scan') {
  steps {
    withCredentials([string(credentialsId: 'fortify-token', variable: 'FORTIFY_TOKEN')]) {
      sh '''
        sourceanalyzer -b mario-game-build python3 -m py_compile mario_like_game.py
        sourceanalyzer -b mario-game-build -scan -f mario-game.fpr
        # Add your upload/reporting step as required by your Fortify environment
      '''
    }
  }
}
```

---

## 6) Create Jenkins Pipeline job

1. In Jenkins dashboard, click **New Item**.
2. Enter name, choose **Pipeline**, click OK.
3. Under **Pipeline definition**, choose:
   - **Pipeline script from SCM**
   - SCM: **Git**
   - Repo URL: your repository URL
   - Branch: e.g. `main`
   - Script path: `Jenkinsfile`
4. Save job.

---

## 7) Run pipeline

1. Click **Build Now**.
2. Watch **Console Output**.
3. Confirm stage success in order:
   - Checkout
   - Install Dependencies
   - Static Checks
   - Mend Scan
   - Fortify Scan
   - Build Docker Image
   - Push Docker Image
   - Deploy Docker Container (Direct)

---

## 8) Verify deployment

On the Jenkins agent/host where Docker deploy runs:

```bash
docker ps | grep mario-game
```

Inspect logs:

```bash
docker logs mario-game
```

---

## 9) Local development run (without Jenkins)

## A. Run directly with Python

```bash
pip install -r requirements.txt
python mario_like_game.py
```

## B. Run with Docker

```bash
docker build -t mario-game:local .
docker run --rm -e SDL_VIDEODRIVER=dummy mario-game:local
```

---

## 10) Common issues

- **`docker: permission denied` in Jenkins**
  - Add Jenkins user to docker group and restart Jenkins/agent.

- **Mend/Fortify command not found**
  - Install tool on the specific Jenkins agent executing pipeline.

- **Scan auth failures**
  - Recheck token credentials IDs and environment variable mapping.

- **Push denied to registry**
  - Verify `DOCKER_CREDENTIALS_ID`, repo permissions, and target image path.

---

## 11) Security recommendations

- Store all tokens/passwords only in Jenkins Credentials (never plaintext in repo).
- Use least-privilege service accounts for Mend/Fortify/registry.
- Rotate credentials regularly.
