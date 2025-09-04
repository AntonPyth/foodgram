# Copilot Instructions for foodgram

## Project Overview
- **foodgram** is a full-stack web application for managing recipes, ingredients, tags, and user accounts.
- The backend is a Django REST Framework (DRF) project (Python 3.9), organized as a monorepo with `backend/` (Django), `frontend/` (React), and `infra/` (deployment).
- The backend uses a modular app structure: `apps/recipe`, `apps/accounts`, `apps/api`.
- The frontend is a React SPA (see `frontend/src/`).
- Docker is used for local and production deployments. See `docker-compose.yml` and `infra/`.

## Key Patterns & Conventions
- **App Imports:** Use absolute imports like `from recipe.models import ...` within backend apps. The `apps/` directory is on the Python path.
- **Serializers:** DRF serializers are in `apps/api/serializers.py`. Tag, Ingredient, and Recipe serialization logic is here. Use `TagSerializer` for tags.
- **API Endpoints:** DRF viewsets and routers are in `apps/api/views.py` and `apps/api/urls.py`. Tags are exposed via `/api/tags/`.
- **Models:** All business logic is in `apps/recipe/models.py` and `apps/accounts/models.py`.
- **Validation:** Custom validation is handled in serializers, e.g., unique tags/ingredients in recipes.
- **Testing:** Use the Postman collection in `postman_collection/` for API contract testing. See its README for reset/cleanup scripts.
- **Frontend Tag Loading:** Tags are loaded from the `/api/tags/` endpoint. If tags do not appear on the create recipe page, check backend endpoint, serializer, and frontend API call.

## Developer Workflows
- **Local Dev:**
  - Use Docker Compose: `docker-compose up --build` from the project root.
  - For backend-only: activate venv, run `python backend/manage.py runserver` from the `backend/` directory.
- **Migrations:**
  - `python backend/manage.py makemigrations`
  - `python backend/manage.py migrate`
- **Testing:**
  - Use Postman collection: see `postman_collection/README.md`.
  - For unit tests: `python backend/manage.py test`
- **Data:**
  - Initial data for ingredients/tags is in `backend/data/`.

## Integration & External Dependencies
- **Docker:** All services (backend, frontend, db, nginx) are containerized.
- **DRF Extra Fields:** Used for image fields (see `Base64ImageField`).
- **Frontend/Backend Contract:** Tag/ingredient/recipe schemas must match between DRF serializers and React components.

## Troubleshooting
- If tags do not load on the frontend, check:
  - `/api/tags/` endpoint (should return a list of tags via `TagSerializer`) 
  - Frontend API call to `/api/tags/`
  - Tag model and migrations
- For import errors, ensure you are running commands from the correct directory and that `apps/` is on the Python path.

## References
- See `README.md` for stack and setup.
- See `postman_collection/README.md` for API testing workflow.
- Key files: `backend/apps/api/serializers.py`, `backend/apps/api/views.py`, `backend/apps/recipe/models.py`, `frontend/src/pages/recipe-create/`, `infra/`.
