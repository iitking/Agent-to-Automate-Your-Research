# API Documentation

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Application status |
| `GET` | `/api/config` | Runtime provider statuses |
| `POST` | `/api/config` | Update runtime API keys |
| `POST` | `/api/research` | Submit research question |
| `GET` | `/api/research` | List user research tasks |
| `GET` | `/api/research/{id}` | Task overview and stats |
| `GET` | `/api/research/{id}/status` | Execution progress and agent logs |
| `GET` | `/api/research/{id}/events` | SSE live progress stream |
| `GET` | `/api/research/{id}/sources` | Retrieved source records |
| `GET` | `/api/research/{id}/findings` | Question-grouped findings |
| `GET` | `/api/research/{id}/claims` | Verified claims and citations |
| `GET` | `/api/research/{id}/report` | Canonical Markdown report |
| `GET` | `/api/research/{id}/export` | Download report (pdf/docx/markdown) |
| `DELETE` | `/api/research/{id}` | Delete task |
