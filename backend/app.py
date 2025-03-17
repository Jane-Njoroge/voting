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

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://van:1234@localhost/voting_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_sessions')
app.config['SESSION_COOKIE_SECURE'] = False  # False for local dev, True for HTTPS production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Lax works for most cross-origin requests
app.config['SESSION_COOKIE_NAME'] = 'session'  # Explicit name for clarity
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session lifetime

# Ensure session directory exists
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# Flask-Mail, Twilio, Uploads (unchanged)
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


@app.route("/debug-session")
def debug_session():
    import os

    session_id = request.cookies.get("session")  
    session_files = os.listdir("./flask_sessions/")  

    return {
        "session_id_from_cookie": session_id,
        "stored_sessions": session_files,
        "current_session_data": dict(session)
    }



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

@app.route('/get_logged_in_user', methods=['GET'])
def get_logged_in_user():
    if 'user_id' in session:
       
        user_details = fetch_user_details_from_db(session['user_id'])
        return jsonify({'full_name': user_details['full_name']})
    else:
        return jsonify({'error': 'User not logged in'}), 401

def fetch_user_details_from_db(user_id):
   
    pass

@app.route('/get_name_profile_image/<int:candidate_id>', methods=['GET'])
def get_name_profile_image(candidate_id):
    if 'candidate_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    candidate = Candidate.query.get(candidate_id)
    if not candidate or candidate.id != session['candidate_id']:
        return jsonify({'error': 'Candidate not found or unauthorized'}), 404

    verification = Verification.query.filter_by(candidate_id=candidate_id).first()
    profile_image = verification.profile_image if verification else None

    return jsonify({
        'full_name': candidate.full_name,
        'profileImage': profile_image
    }), 200



@app.route('/get_votes', methods=['GET'])
def get_votes():
    votes = Votes.query.all()
    votes_list = [
        {
            "id": v.id,
            "candidate_id": v.candidate_id,
            "voter_phone": v.voter_phone
        }
        for v in votes
    ]
    return jsonify({"votes": votes_list}), 200


@app.route('/ussd_vote', methods=['POST'])
def ussd_vote():
    data = request.get_json()
    voter_phone = data.get('voter_phone')
    candidate_id = data.get('candidate_id')

    if not voter_phone or not candidate_id:
        return jsonify({'error': 'Voter phone and candidate ID are required'}), 400

    existing_vote = Votes.query.filter_by(voter_phone=voter_phone).first()
    if existing_vote:
        return jsonify({'error': 'Voter has already voted'}), 400

    new_vote = Votes(voter_phone=voter_phone, candidate_id=candidate_id)
    db.session.add(new_vote)
    db.session.commit()

    return jsonify({'message': 'Vote recorded successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)