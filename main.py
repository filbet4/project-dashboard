from fastapi import FastAPI
from app.database import Base, engine
from app.routes.users import router as users_router
from app.routes.projects import router as projects_router
from app.routes.documents import router as documents_router
from app.routes.members import router as members_router
from contextlib import asynccontextmanager

# This runs the CREATE TABLE statements based on our models

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the application starts.
    """


    yield
    
# Create the FastAPI application instance
app = FastAPI(
    title="Project Dashboard API",
    description="A collaborative project management backend",
    version="0.1.0",
    lifespan=lifespan
)


    # Code placed here would run during application shutdown.
app.include_router(documents_router)
# Include user routes
# This registers all the endpoints from users.py under /users
app.include_router(users_router)

# Include project routes
# This registers all the endpoints from projects.py under /projects
app.include_router(projects_router)
app.include_router(members_router)

# Define a simple endpoint 
@app.get("/")
def read_root():
    """
    Simple hello world endpoint.
    This responds to GET requests at the root URL (/)
    """
    return {"message": "Hello World! Project Dashboard API is running"}


# Health check endpoint (useful for monitoring)
@app.get("/health")
def health_check():
    """
    Endpoint to check if the API is running
    Responds with a status message
    """
    return {"status": "ok"}


# This runs the app locally if you execute this file directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
