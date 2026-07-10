# Project Structure

```text
industrial-knowledge-copilot/
|-- README.md
|-- requirements.txt
|-- .env.example
|-- docs/
|   |-- project-structure.md
|   |-- architecture-plan.md
|   |-- database-schema.md
|   |-- api-endpoints.md
|   `-- development-roadmap.md
|-- src/
|   |-- __init__.py
|   |-- main.py
|   |-- api/
|   |   |-- __init__.py
|   |   `-- v1/
|   |       `-- __init__.py
|   |-- core/
|   |   `-- __init__.py
|   |-- db/
|   |   `-- __init__.py
|   |-- models/
|   |   `-- __init__.py
|   |-- schemas/
|   |   `-- __init__.py
|   |-- services/
|   |   `-- __init__.py
|   |-- agents/
|   |   `-- __init__.py
|   |-- retrieval/
|   |   `-- __init__.py
|   |-- ingestion/
|   |   `-- __init__.py
|   `-- utils/
|       `-- __init__.py
|-- tests/
|   |-- __init__.py
|   |-- unit/
|   |   `-- __init__.py
|   |-- integration/
|   |   `-- __init__.py
|   `-- e2e/
|       `-- __init__.py
|-- scripts/
|   `-- .gitkeep
|-- data/
|   |-- raw/
|   |   `-- .gitkeep
|   |-- processed/
|   |   `-- .gitkeep
|   `-- vector_index/
|       `-- .gitkeep
`-- infra/
    |-- docker/
    |   `-- .gitkeep
    `-- k8s/
        `-- .gitkeep
```

