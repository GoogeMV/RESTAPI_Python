# University Services Project — Schedules module

REST API built as a **ten-person team project** for the Service Oriented Systems course (Computer Science and Engineering, "Dunărea de Jos" University of Galați, 2025–2026).

The system exposes a set of independent modules for a university management domain: `announcements`, `auth`, `enrollments`, `grades`, `library`, `materials`, `professors`, `reports` and `schedule`.

**I owned the `schedule` module** end to end: endpoint design, OpenAPI specification, implementation, unit tests and documentation.

> **About this repository:** the project was developed on the university's self-hosted GitLab, which is private and not reachable from outside. This repository is a snapshot of the final state, so the commit history here does not reflect the actual work. The real history — 272 commits across 41 branches — lives on GitLab. Screenshots below.

---

## How the team worked

Nobody pushed to `main`. Every change went through the same loop:

1. Branch off `main` (`feature/schedule-tests`, `features/openapijson`, and so on).
2. Open a merge request.
3. The CI pipeline runs automatically on the branch.
4. A teammate reviews and approves.
5. Merge.

Commit and MR titles followed a `type: description` convention (`docs:`, `spec:`, `fix:`, `chore:`).

I opened 8 merge requests, all reviewed, approved and merged.

## CI pipeline

Two stages, running on `python:3.12-slim`, triggered on every push:

| Stage | What runs |
| --- | --- |
| `lint` | `ruff check` and `ruff format --check` (non-blocking, reports only) |
| `test` | `pytest` across the whole suite, 162 tests |

The test stage emits a JUnit XML report declared as a GitLab artifact, so the pass/fail summary appears directly inside each merge request rather than only in the job log. Pip dependencies are cached between runs.

Pipeline configuration ([`.gitlab-ci.yml`](.gitlab-ci.yml)):

```yaml
image: python:3.12-slim
stages:
  - lint
  - test
variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"
cache:
  paths:
    - .pip-cache/
before_script:
  - pip install -r requirements.txt
  - pip install pytest ruff httpx
lint:
  stage: lint
  script:
    - ruff check .
    - ruff format --check .
  allow_failure: true
test:
  stage: test
  script:
    - pytest ./tests/ -v --junitxml=report.xml --tb=short
  artifacts:
    when: always
    reports:
      junit: report.xml
    paths:
      - report.xml
    expire_in: 30 days
```

I did not author this configuration myself, but every change I made went through it.

---

## Evidence from GitLab
<img width="1568" height="737" alt="image" src="https://github.com/user-attachments/assets/03fc4981-5396-4a58-ba7b-446367de4702" />
One of my merge requests, end to end. Branch feature/schedule-tests into main: pipeline #1914 passed, approved by a teammate, 162 tests reported by the JUnit artifact directly in the MR, then merged by a reviewer.
<img width="1568" height="741" alt="image" src="https://github.com/user-attachments/assets/a0d1a1fb-3438-4e36-acc5-0c57192fb334" />
All eight of my merge requests on the project, every one reviewed, approved and merged. No direct pushes to main.

## What I took from it

Working in a shared repository with nine other people changes how you write code. An endpoint isn't done when it works on your machine — it's done when the spec is written, the tests pass in CI, and someone else has read the diff and agreed with it. The `schedule` module went through that cycle for every change.
