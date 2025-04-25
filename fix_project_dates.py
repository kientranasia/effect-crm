from app import create_app
from app.extensions import db
from app.models.project import Project
from datetime import datetime, date
import sqlite3
import os

def fix_project_dates():
    """Fix project date fields in the database"""
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
        
        # Fix each project's date fields
        for project_id, start_date, end_date in projects:
            # Fix start_date
            if start_date is not None:
                try:
                    if isinstance(start_date, int):
                        # Convert year to January 1st of that year
                        new_start_date = date(start_date, 1, 1).isoformat()
                    else:
                        new_start_date = start_date
                    cursor.execute(
                        "UPDATE projects SET start_date = ? WHERE id = ?",
                        (new_start_date, project_id)
                    )
                except Exception as e:
                    print(f"Error fixing start_date for project {project_id}: {e}")
            
            # Fix end_date
            if end_date is not None:
                try:
                    if isinstance(end_date, int):
                        # Convert year to December 31st of that year
                        new_end_date = date(end_date, 12, 31).isoformat()
                    else:
                        new_end_date = end_date
                    cursor.execute(
                        "UPDATE projects SET end_date = ? WHERE id = ?",
                        (new_end_date, project_id)
                    )
                except Exception as e:
                    print(f"Error fixing end_date for project {project_id}: {e}")
        
        # Commit the changes
        conn.commit()
        conn.close()
        
        print("Project date fields have been fixed.")

if __name__ == "__main__":
    fix_project_dates() 