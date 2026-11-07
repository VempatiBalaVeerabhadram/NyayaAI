# NyayaAI Deployment & Operations Manual

## 1. Local Development Mode

### Starting Databases via Docker:
```bash
docker compose up -d mongodb neo4j qdrant
```

Verify services:
- MongoDB: `localhost:27017`
- Neo4j Browser: `http://localhost:7474`
- Qdrant REST: `http://localhost:6333/dashboard`

### Starting Backend:
```bash
cd backend
npm run dev
```

### Starting AI Service:
```bash
cd ai-service
# activate virtual environment
./venv/Scripts/activate # Windows
source venv/bin/activate # Linux/Mac
uvicorn main:app --reload --port 8000
```

### Starting Frontend:
```bash
cd frontend
npm run dev
```

---

## 2. Full Containerized Deployment

To build and run the entire stack with a single command:
```bash
docker compose up --build -d
```
All services run inside a dedicated bridge network `nyayaai-network` with automated service discovery and health checks.
