import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from extensions import db, migrate  # <<< We import from extensions.py
from flask_cors import CORS

# Import our AI Service
import ai_service

def create_app():
    """
    Application Factory Pattern:
    This function creates and configures the Flask application.
    """
    
    app = Flask(__name__)
    
    # Load Configuration from .env
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions WITH the app
    # This links our 'db' and 'migrate' objects to our 'app' instance
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # We MUST import the models *after* db.init_app()
    # This registers the models with SQLAlchemy for the app
    from models import User, Project, Analysis

    # --- Register API Routes ---
    # We define the routes *inside* the factory so they
    # are part of the app's context.
    
    @app.route('/')
    def home():
        return "SDLC AI Assistant Backend is running."

    # --- Project Endpoints ---
    
    @app.route('/api/project', methods=['POST'])
    def create_project():
        """
        Creates a new project.
        Expects JSON: { "name": "My Project Name" }
        """
        data = request.json
        if not data or 'name' not in data:
            return jsonify({"error": "Missing 'name' in request"}), 400
        
        new_project = Project(name=data['name'])
        db.session.add(new_project)
        db.session.commit()
        
        print(f"Created new project (ID: {new_project.id}): {new_project.name}")
        return jsonify(new_project.to_dict()), 201

    @app.route('/api/project/<int:project_id>', methods=['GET'])
    def get_project(project_id):
        """
        Gets details for a single project.
        """
        # This query will now work because 'db' is correctly initialized
        project = Project.query.get_or_404(project_id)
        return jsonify(project.to_dict())


    # --- Analysis Endpoint for PS-01 ---

    @app.route('/api/project/<int:project_id>/analyze-tradeoff', methods=['POST'])
    def analyze_tradeoff(project_id):
        """
        Runs the PS-01 Trade-off Analysis.
        """
        # This was the line that failed. It will now work
        # because it is running inside the app context.
        project = Project.query.get_or_404(project_id)
        
        # Get input data from the request body
        data = request.json
        if not data or 'option1' not in data or 'option2' not in data or 'criteria' not in data:
            return jsonify({"error": "Missing option1, option2, or criteria"}), 400
            
        option1 = data['option1']
        option2 = data['option2']
        criteria = data['criteria']

        try:
            # Call our AI "Brain"
            print(f"Starting trade-off analysis for project {project.name}...")
            generated_text = ai_service.perform_tradeoff_analysis(option1, option2, criteria)
            
            # Save the inputs and the result to our database
            new_analysis = Analysis(
                project_id=project.id,
                analysis_type="PS-01_TRADEOFF",
                input_data=data,  # Store the JSON we received
                generated_content=generated_text
            )
            
            db.session.add(new_analysis)
            db.session.commit()
            
            print(f"Analysis {new_analysis.id} saved to database.")
            
            # Return the full Analysis object to the user
            return jsonify(new_analysis.to_dict()), 201
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            return jsonify({"error": "An internal server error occurred"}), 500
# --- Analysis Endpoint for PS-02 ---
        
    @app.route('/api/project/<int:project_id>/review-design', methods=['POST'])
    def review_design(project_id):
            """
            Runs the PS-02 Design Review.
            Expects JSON: { "document": "..." }
            """
            # 1. Find the project in the database
            project = Project.query.get_or_404(project_id)
            
            # 2. Get input data from the request body
            data = request.json
            if not data or 'document' not in data:
                return jsonify({"error": "Missing 'document' text"}), 400
                
            document_text = data['document']

            try:
                # 3. Call our AI "Brain" (the new function)
                print(f"Starting design review for project {project.name}...")
                generated_text = ai_service.perform_design_review(document_text)
                
                # 4. Save the result to our database
                new_analysis = Analysis(
                    project_id=project.id,
                    analysis_type="PS-02_DESIGN_REVIEW", # <-- New type
                    input_data=data,  # Store the input document
                    generated_content=generated_text
                )
                
                db.session.add(new_analysis)
                db.session.commit()
                
                print(f"Analysis {new_analysis.id} saved to database.")
                
                # 5. Return the full Analysis object to the user
                return jsonify(new_analysis.to_dict()), 201
                
            except Exception as e:
                print(f"Error during analysis: {e}")
                return jsonify({"error": "An internal server error occurred"}), 500

    # This 'return app' line should be at the very end
    return app    
   
# --- Main entry point to run the app ---
# app/main.py
from . import create_app
import os

app = create_app()

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("APP_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)
