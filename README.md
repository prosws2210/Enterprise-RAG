# Enterprise RAG

Welcome to the Enterprise RAG project. The codebase has been organized into logical components to reduce clutter.

## Directory Structure

- `/backend/`: Contains the FastAPI application, background scripts, evaluation tools, and database seeding logic.
- `/frontend/`: Contains the React/Vite web interface.
- `/others/`: Contains Jupyter notebooks, original project reports, and full documentation.

## Running the Application

### Using Docker Compose (Recommended)
You can start the entire stack (Postgres, Qdrant, Redis if configured, and Backend API) by running:
```bash
docker compose up -d --build
```
Then start the frontend:
```bash
cd frontend
npm run dev
```

For more detailed information, see the full README in `others/README.md`.
