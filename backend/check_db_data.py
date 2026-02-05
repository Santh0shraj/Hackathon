
from app import create_app
from database import db
from models import Workflow

app = create_app()

def check_data():
    with app.app_context():
        try:
            workflows = Workflow.query.all()
            print(f"--- Database Verification ---")
            print(f"Total Workflows found: {len(workflows)}")
            for wf in workflows:
                print(f"ID: {wf.id} | Name: {wf.name} | Created: {wf.created_at}")
        except Exception as e:
            print(f"Error querying database: {e}")

if __name__ == "__main__":
    check_data()
