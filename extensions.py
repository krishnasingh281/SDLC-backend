from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create the extension instances here
# They are not attached to any app yet.
# This file ensures we only have ONE instance of db and migrate.
db = SQLAlchemy()
migrate = Migrate()
