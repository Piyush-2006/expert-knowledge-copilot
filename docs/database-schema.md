# Database Schema - Expert Knowledge Copilot

Primary store: PostgreSQL  
Vector extension: pgvector

## 1) users

- `id` (uuid, pk)
- `email` (varchar, unique, not null)
- `full_name` (varchar)
- `role` (varchar) - `admin | expert | operator | viewer`
- `is_active` (boolean, default true)
- `created_at` (timestamp)
- `updated_at` (timestamp)

## 2) workspaces

- `id` (uuid, pk)
- `name` (varchar, not null)
- `industry_domain` (varchar)
- `owner_user_id` (uuid, fk -> users.id)
- `created_at` (timestamp)
- `updated_at` (timestamp)

## 3) knowledge_sources

- `id` (uuid, pk)
- `workspace_id` (uuid, fk -> workspaces.id)
- `source_type` (varchar) - `upload | sharepoint | s3 | confluence | manual`
- `name` (varchar, not null)
- `uri` (text)
- `status` (varchar) - `active | paused | error`
- `last_synced_at` (timestamp, nullable)
- `created_by` (uuid, fk -> users.id)
- `created_at` (timestamp)

## 4) documents

- `id` (uuid, pk)
- `workspace_id` (uuid, fk -> workspaces.id)
- `source_id` (uuid, fk -> knowledge_sources.id)
- `title` (varchar, not null)
- `doc_type` (varchar) - `sop | manual | report | incident | faq | other`
- `external_ref` (varchar, nullable)
- `version_label` (varchar, nullable)
- `checksum` (varchar, not null)
- `status` (varchar) - `indexed | pending | failed | archived`
- `metadata_json` (jsonb)
- `created_at` (timestamp)
- `updated_at` (timestamp)

## 5) document_chunks

- `id` (uuid, pk)
- `document_id` (uuid, fk -> documents.id)
- `chunk_index` (integer, not null)
- `content` (text, not null)
- `token_count` (integer)
- `embedding` (vector(1536))  // dimensionality configurable
- `chunk_metadata_json` (jsonb)
- `created_at` (timestamp)

Indexes:
- unique (`document_id`, `chunk_index`)
- ivfflat or hnsw index on `embedding`

## 6) conversations

- `id` (uuid, pk)
- `workspace_id` (uuid, fk -> workspaces.id)
- `user_id` (uuid, fk -> users.id)
- `title` (varchar)
- `status` (varchar) - `active | closed`
- `created_at` (timestamp)
- `updated_at` (timestamp)

## 7) messages

- `id` (uuid, pk)
- `conversation_id` (uuid, fk -> conversations.id)
- `sender_type` (varchar) - `user | assistant | system`
- `content` (text, not null)
- `citations_json` (jsonb, nullable)
- `confidence_score` (numeric(5,4), nullable)
- `latency_ms` (integer, nullable)
- `created_at` (timestamp)

## 8) feedback

- `id` (uuid, pk)
- `message_id` (uuid, fk -> messages.id)
- `user_id` (uuid, fk -> users.id)
- `rating` (smallint) - `1..5`
- `label` (varchar) - `helpful | inaccurate | unsafe | incomplete`
- `comment` (text, nullable)
- `created_at` (timestamp)

## 9) ingestion_jobs

- `id` (uuid, pk)
- `workspace_id` (uuid, fk -> workspaces.id)
- `source_id` (uuid, fk -> knowledge_sources.id)
- `job_type` (varchar) - `sync | reindex | delete`
- `status` (varchar) - `queued | running | completed | failed`
- `started_at` (timestamp, nullable)
- `finished_at` (timestamp, nullable)
- `error_message` (text, nullable)
- `stats_json` (jsonb, nullable)
- `created_at` (timestamp)

## 10) audit_logs

- `id` (uuid, pk)
- `workspace_id` (uuid, fk -> workspaces.id)
- `actor_user_id` (uuid, fk -> users.id, nullable)
- `action` (varchar, not null)
- `target_type` (varchar, nullable)
- `target_id` (uuid, nullable)
- `details_json` (jsonb, nullable)
- `created_at` (timestamp)

## Suggested Initial ER Relationships

- One workspace has many sources, documents, conversations, and jobs.
- One document has many chunks.
- One conversation has many messages.
- One message can have many feedback entries (or constrain to one per user by unique index).

