from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Define Flask application factory function
def create_app():
    app = Flask(__name__)

    # Configure SQLite database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../subway_outlets.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with the Flask application context
    db.init_app(app)

    return app

# Define your database models
class Outlet(db.Model):
    __tablename__ = 'outlets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    waze_link = db.Column(db.String)
    latitude = db.Column(db.Float)  
    longitude = db.Column(db.Float)

    # One-to-Many relationship with OpeningHours
    opening_hours = db.relationship('OpeningHours', back_populates='outlet')

class OpeningHours(db.Model):
    __tablename__ = 'opening_hours'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)  # Store opening hours as formatted text
    outlet_id = db.Column(db.Integer, db.ForeignKey('outlets.id'))

    # Define relationship back to Outlet
    outlet = db.relationship('Outlet', back_populates='opening_hours')
