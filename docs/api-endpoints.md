# API Endpoints - Expert Knowledge Copilot (v1)

Base path: `/api/v1`

## Health and System

- `GET /health` - service health
- `GET /ready` - readiness (db/vector store/worker dependencies)
- `GET /metrics` - Prometheus metrics

## Auth and Users

- `POST /auth/login` - issue access token
- `POST /auth/refresh` - refresh token
- `GET /users/me` - current user profile
- `GET /users` - list users (admin)
- `POST /users` - create user (admin)

## Workspaces

- `GET /workspaces`
- `POST /workspaces`
- `GET /workspaces/{workspace_id}`
- `PATCH /workspaces/{workspace_id}`
- `DELETE /workspaces/{workspace_id}`

## Knowledge Sources

- `GET /workspaces/{workspace_id}/sources`
- `POST /workspaces/{workspace_id}/sources`
- `GET /workspaces/{workspace_id}/sources/{source_id}`
- `PATCH /workspaces/{workspace_id}/sources/{source_id}`
- `DELETE /workspaces/{workspace_id}/sources/{source_id}`
- `POST /workspaces/{workspace_id}/sources/{source_id}/sync`

## Documents and Ingestion

- `GET /workspaces/{workspace_id}/documents`
- `POST /workspaces/{workspace_id}/documents/upload`
- `GET /workspaces/{workspace_id}/documents/{document_id}`
- `DELETE /workspaces/{workspace_id}/documents/{document_id}`
- `POST /workspaces/{workspace_id}/documents/{document_id}/reindex`
- `GET /workspaces/{workspace_id}/jobs`
- `GET /workspaces/{workspace_id}/jobs/{job_id}`

## Copilot Chat

- `POST /workspaces/{workspace_id}/chat/conversations`
- `GET /workspaces/{workspace_id}/chat/conversations/{conversation_id}`
- `POST /workspaces/{workspace_id}/chat/conversations/{conversation_id}/messages`
- `GET /workspaces/{workspace_id}/chat/conversations/{conversation_id}/messages`

Expected message response payload:
- assistant answer text
- citation list (`document_id`, `chunk_id`, `excerpt`, `score`)
- confidence score
- trace id

## Retrieval and Search

- `POST /workspaces/{workspace_id}/search`
- `POST /workspaces/{workspace_id}/retrieve/debug` (admin/expert only)

## Feedback and Evaluation

- `POST /workspaces/{workspace_id}/feedback`
- `GET /workspaces/{workspace_id}/feedback`
- `GET /workspaces/{workspace_id}/analytics/quality`

## Admin and Audit

- `GET /workspaces/{workspace_id}/audit-logs`
- `GET /workspaces/{workspace_id}/settings`
- `PATCH /workspaces/{workspace_id}/settings`

## API Conventions

- Auth: `Authorization: Bearer <token>`
- Pagination: `page`, `page_size` or cursor-based for large sets
- Idempotency key on write-heavy endpoints
- Error format:
  - `code`
  - `message`
  - `details`
  - `trace_id`

