# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the API router
from .api import game_routes # Use relative import
# Import database setup and models
from .db import database, models

# Create DB tables if they don't exist
# Note: In production, you might use Alembic for migrations
# This line ensures tables are created when the app starts
models.Base.metadata.create_all(bind=database.engine)


app = FastAPI(title="Text RPG API")

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:8080", 
    "http://127.0.0.1:5500", # VS Code Live Server default
    "null", 
    # Add any other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Include the game API router
app.include_router(game_routes.router, prefix="/api/v1") # Added a version prefix

# Simple root endpoint for testing
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Text RPG API!"}

# The main logic for /start_game and /make_choice is now in api/game_routes.py
# and services/game_service.py

if __name__ == "__main__":
    import uvicorn
    # This allows running directly for debugging, but use start.py for normal execution
    print("Starting server directly. Use 'python start.py' for normal execution.")
    # Note: Relative imports might behave differently when run directly vs via uvicorn from root
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
