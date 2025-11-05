from extensions import db  # <<< CHANGE THIS LINE
from datetime import datetime, timezone
import json

# --- THE REST OF THIS FILE STAYS EXACTLY THE SAME ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # This 'relationship' links this User to all their Projects
    projects = db.relationship('Project', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # This 'ForeignKey' links this project to a specific User's id.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # This 'relationship' links this Project to all its Analyses.
    analyses = db.relationship('Analysis', backref='project', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        """Returns a dictionary representation for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id
        }

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # This 'ForeignKey' links this Analysis to a specific Project's id.
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    # This is the "type" (e.g., 'PS-01_TRADEOFF', 'PS-07_CODE_REVIEW')
    analysis_type = db.Column(db.String(50), nullable=False)
    
    _input_data_json = db.Column("input_data", db.Text, nullable=True)
    
    # This is the AI's output (the Markdown report)
    generated_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def input_data(self):
        """Loads the JSON string from the DB as a Python dict."""
        if self._input_data_json is None:
            return {}
        return json.loads(self._input_data_json)

    @input_data.setter
    def input_data(self, value):
        """Saves a Python dict as a JSON string in the DB."""
        self._input_data_json = json.dumps(value)

    def to_dict(self):
        """Returns a dictionary representation for API responses."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "analysis_type": self.analysis_type,
            "input_data": self.input_data, # Uses the @property
            "generated_content": self.generated_content,
            "timestamp": self.timestamp.isoformat()
        }
