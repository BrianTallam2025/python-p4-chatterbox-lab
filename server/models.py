from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()

class Message(db.Model, SerializerMixin):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Serialize rules to prevent recursion (not strictly needed here but good practice)
    # or to control which fields are exposed.
    # For this lab, we want all fields to be serialized implicitly.
    # If you had relationships, you might use:
    # serialize_rules = ('-relationship_name.messages',)

    def __repr__(self):
        return f'<Message {self.id}: {self.username} - {self.body[:20]}...>'