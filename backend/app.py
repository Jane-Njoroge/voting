from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv
from twilio.rest import Client
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging

load_dotenv()

app = Flask(__name__)

# Configuration (unchanged)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://van:1234@localhost/voting_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_sessions')
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads/profile_folder')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"], allow_headers=["Content-Type", "Authorization"])
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

logging.basicConfig(level=logging.DEBUG)

# Models (unchanged)
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    forgot_password = db.Column(db.String(255), nullable=True)
    verifications = db.relationship('Verification', backref='candidate', lazy=True)
    votes = db.relationship('Votes', backref='candidate', lazy=True)

class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    national_id = db.Column(db.String(50), unique=True, nullable=False)
    profile_image = db.Column(db.String(255), nullable=True, default='default.jpg')
    is_verified = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(200), nullable=False, default='Uncategorized')
    vote_count = db.Column(db.Integer, default=0)

class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    voter_phone = db.Column(db.String(20), nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Existing Routes (unchanged)
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')

    if not full_name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    existing_user = Candidate.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User already exists, please log in'}), 400
    
    hashed_password = generate_password_hash(password)
    new_candidate = Candidate(full_name=full_name, email=email, password=hashed_password)
    db.session.add(new_candidate)
    db.session.commit()
    session['candidate_id'] = new_candidate.id
    return jsonify({'message': 'Signup successful!', 'candidate_id': new_candidate.id}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'error': 'Email and password are required'}), 400

    user = Candidate.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    session['candidate_id'] = user.id
    session.permanent = True 
    logging.debug(f"Login: Set session['candidate_id'] = {user.id}")
    return jsonify({'message': 'Login successful!', 'candidate_id': user.id}), 200

@app.route('/check-session', methods=['GET'])
def check_session():
    logging.debug(f"Check-session: Session data = {session}")
    if 'candidate_id' in session:
        return jsonify({'message': 'Session active', 'user_id': session['candidate_id']}), 200
    return jsonify({'error': 'No active session'}), 401

@app.route('/assign_category', methods=['POST'])
def assign_category():
    data = request.get_json()
    candidate_id = data.get('candidate_id')
    category = data.get('category')

    if not all([candidate_id, category]):
        return jsonify({'error': 'Candidate ID and category are required'}), 400

    verification = Verification.query.filter_by(candidate_id=candidate_id).first()
    if not verification:
        verification = Verification(candidate_id=candidate_id, phone_number='', national_id='', category=category)
        db.session.add(verification)
    else:
        verification.category = category
    db.session.commit()
    return jsonify({'message': 'Category assigned successfully'}), 200

# Add this new route to fetch the logged-in candidate's profile
@app.route('/get_my_profile', methods=['GET'])
def get_my_profile():
    if 'candidate_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    candidate = Candidate.query.get(session['candidate_id'])
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404

    verification = Verification.query.filter_by(candidate_id=session['candidate_id']).first()
    profile_image = verification.profile_image if verification and verification.profile_image != 'default.jpg' else None

    return jsonify({
        'full_name': candidate.full_name,
        'profileImage': profile_image
    }), 200

# @app.route('/get_name_profile_image/<int:candidate_id>', methods=['GET'])
# def get_name_profile_image(candidate_id):
#     if 'candidate_id' not in session:
#         return jsonify({'error': 'User not logged in'}), 401

#     candidate = Candidate.query.get(candidate_id)
#     if not candidate or candidate.id != session['candidate_id']:
#         return jsonify({'error': 'Candidate not found or unauthorized'}), 404

#     verification = Verification.query.filter_by(candidate_id=candidate_id).first()
#     profile_image = verification.profile_image if verification and verification.profile_image != 'default.jpg' else None

#     return jsonify({
#         'full_name': candidate.full_name,
#         'profileImage': profile_image
#     }), 200

@app.route('/upload_profile_image/<int:candidate_id>', methods=['POST'])
def upload_profile_image(candidate_id):
    if 'candidate_id' not in session or session['candidate_id'] != candidate_id:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'profile_image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['profile_image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{candidate_id}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        verification = Verification.query.filter_by(candidate_id=candidate_id).first()
        if not verification:
            verification = Verification(candidate_id=candidate_id, phone_number='', national_id='', profile_image=filename)
            db.session.add(verification)
        else:
            # Remove old image if it exists and isn't default
            if verification.profile_image and verification.profile_image != 'default.jpg':
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], verification.profile_image)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            verification.profile_image = filename
        db.session.commit()

        return jsonify({'message': 'Image uploaded successfully', 'profileImage': filename}), 200
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/candidate/<int:candidate_id>/votes', methods=['GET'])
def get_candidate_votes(candidate_id):
    verification = Verification.query.filter_by(candidate_id=candidate_id).first()
    if not verification:
        return jsonify({'vote_count': 0}), 200
    return jsonify({'vote_count': verification.vote_count}), 200

@app.route('/delete_profile_image/<int:candidate_id>', methods=['DELETE'])
def delete_profile_image(candidate_id):
    if 'candidate_id' not in session or session['candidate_id'] != candidate_id:
        return jsonify({'error': 'Unauthorized'}), 401

    verification = Verification.query.filter_by(candidate_id=candidate_id).first()
    if not verification or not verification.profile_image or verification.profile_image == 'default.jpg':
        return jsonify({'message': 'No profile image to delete'}), 200

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], verification.profile_image)
    if os.path.exists(file_path):
        os.remove(file_path)

    verification.profile_image = 'default.jpg'
    db.session.commit()
    return jsonify({'message': 'Profile image deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)