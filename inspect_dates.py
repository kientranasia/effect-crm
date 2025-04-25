from app import create_app
from app.extensions import db
from app.models.project import Project
import sqlite3
import os

def inspect_dates():
    """Inspect project date fields in the database"""
    app = create_app()
    with app.app_context():
        # Get the database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Connect directly to SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all projects
        cursor.execute("SELECT id, start_date, end_date FROM projects")
        projects = cursor.fetchall()
        
        print("\nProject Dates in Database:")
        print("-" * 50)
        for project_id, start_date, end_date in projects:
            print(f"Project ID: {project_id}")
            print(f"Start Date: {start_date} (type: {type(start_date)})")
            print(f"End Date: {end_date} (type: {type(end_date)})")
            print("-" * 50)
        
        conn.close()

if __name__ == "__main__":
    inspect_dates() 