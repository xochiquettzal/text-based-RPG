# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Define the path for the SQLite database file within the backend directory
# database.py (db) -> backend -> game_database.db
DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite+pysqlite:///{os.path.join(DATABASE_DIR, '..', 'game_database.db')}"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db" # Example for PostgreSQL

# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is needed only for SQLite.
# It allows more than one thread to communicate with the database, which is
# necessary because FastAPI can interact with the database in multiple threads.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class
# Each instance of SessionLocal will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class
# We will inherit from this class to create each of the database models (ORM models).
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """
    FastAPI dependency that provides a database session per request.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_database_tables():
    """Creates all database tables defined inheriting from Base."""
    # This should be called once, e.g., on application startup or via a script.
    # Be careful with this in production if using migrations.
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully (if they didn't exist).")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# You might want to call create_database_tables() from main.py on startup,
# or have a separate script/command to initialize the DB.
# Example for main.py:
# from .db import database
# @app.on_event("startup")
# def on_startup():
#     database.create_database_tables()
