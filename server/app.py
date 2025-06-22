from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, Message # Import your Message model
from datetime import datetime # Import datetime for potential error messages

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False # For pretty JSON output (more readable in browser/Postman)

CORS(app) # Enable CORS for your app

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Chatterbox API</h1>'

# --- Message Routes ---

@app.route('/messages', methods=['GET'])
def get_messages():
    # GET /messages: returns an array of all messages as JSON,
    # ordered by created_at in ascending order.
    messages = Message.query.order_by(Message.created_at.asc()).all()
    # Using serialize() from SerializerMixin to convert objects to dictionaries
    messages_dict = [message.to_dict() for message in messages]
    return make_response(jsonify(messages_dict), 200)

@app.route('/messages', methods=['POST'])
def create_message():
    # POST /messages: creates a new message with a body and username from params,
    # and returns the newly created post as JSON.
    data = request.get_json()

    if not data:
        return make_response(jsonify({"errors": ["No data provided in request body"]}), 400)

    try:
        new_message = Message(
            body=data.get('body'),
            username=data.get('username')
            # created_at and updated_at will be set by default
        )
        db.session.add(new_message)
        db.session.commit()
        return make_response(jsonify(new_message.to_dict()), 201) # 201 Created
    except Exception as e:
        db.session.rollback() # Rollback in case of an error
        return make_response(jsonify({"errors": [str(e)]}), 400) # 400 Bad Request if data is missing/invalid

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    # PATCH /messages/<int:id>: updates the body of the message using params,
    # and returns the updated message as JSON.
    message = Message.query.get(id)

    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404) # 404 Not Found

    data = request.get_json()
    if not data:
        return make_response(jsonify({"errors": ["No data provided for update"]}), 400)

    try:
        # Only update the 'body' as per instructions
        if 'body' in data:
            message.body = data['body']
        # updated_at will be automatically updated by the onupdate argument in the model

        db.session.add(message) # Add to session for update tracking
        db.session.commit()
        return make_response(jsonify(message.to_dict()), 200) # 200 OK
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"errors": [str(e)]}), 400)

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    # DELETE /messages/<int:id>: deletes the message from the database.
    message = Message.query.get(id)

    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404) # 404 Not Found

    try:
        db.session.delete(message)
        db.session.commit()
        return make_response(jsonify({}), 204) # 204 No Content for successful deletion
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"errors": [str(e)]}), 500) # 500 Internal Server Error for unexpected issues


if __name__ == '__main__':
    app.run(port=5000, debug=True)