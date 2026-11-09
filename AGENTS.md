# Workshop project boundaries

This repository contains four independent training projects and their training documentation.
Before editing an application, open that application's folder and read its own AGENTS.md,
constitution, active spec, plan and tasks. Each application uses its own uv.lock and .venv.
Do not create a root uv workspace or copy business implementations between starter and completed projects.
Starter exercises must not search or read the adjacent completed application.
Application MCP credentials remain local. Never commit secrets or local databases.
The root .github/workflows/ci.yml runs all four projects offline; it does not deploy.
Do not commit, push or publish without a user instruction.
