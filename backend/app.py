from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv
from flask import redirect, url_for
from twilio.rest import Client
import random
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging

load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://van:1234@localhost/voting_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Uploads Configuration
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), 'uploads/profile_folder'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])  # Adjust to your frontend URL
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Debugging
app.config['DEBUG'] = True
logging.basicConfig(level=logging.DEBUG)

# Session Cookie Configuration
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production for HTTPS


# Database Models
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    forgot_password = db.Column(db.String(255), nullable=True)
    verifications = db.relationship('Verification', backref='candidate', lazy=True)
    votes = db.relationship('Votes', backref='candidate', lazy=True)

    def __repr__(self):
        return f'<Candidate {self.id}: {self.email}>'


class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    national_id = db.Column(db.String(50), unique=True, nullable=False)
    profile_image = db.Column(db.String(255), nullable=True, default='default.jpg')
    is_verified = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(200), nullable=False, default='Uncategorized')
    vote_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Verification {self.id} for Candidate {self.candidate_id}>'


class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    voter_phone = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Vote {self.id} for Candidate {self.candidate_id}>'


# Helper Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Routes
@app.route('/')
def home():
    return "Voting Backend is Running!"


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
    
    print(f"New candidate {new_candidate} created.")

    return jsonify({'message': 'Signup successful!', 'candidate_id': new_candidate.id}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    logging.debug(f"Received login request with data: {data}")

    if not email or not password:
        logging.warning("Email or password missing in login request.")
        return jsonify({'error': 'Email and password are required'}), 400

    user = Candidate.query.filter_by(email=email).first()

    if user is None:
        logging.warning(f"No user found with email: {email}")
        return jsonify({'error': 'Invalid email or password'}), 401

    if check_password_hash(user.password, password):
        session['candidate_id'] = user.id
        logging.info(f"User {user.email} logged in successfully. Setting session['candidate_id'] = {user.id}")
        return jsonify({'message': 'Login successful!', 'candidate_id': user.id}), 200
    else:
        logging.warning(f"Password incorrect for user: {email}")
        return jsonify({'error': 'Invalid email or password'}), 401


@app.route("/check-session")
def check_session():
    logging.debug(f"Checking session. Current session data: {session}")
    if 'candidate_id' in session:
        logging.info(f"Session active. User ID: {session['candidate_id']}")
        return jsonify({"message": "Session Active", "user_id": session['candidate_id']}), 200
    else:
        logging.info("No active session found.")
        return jsonify({"error": "No Active Session"}), 401


@app.route("/debug-session")
def debug_session():
    logging.debug("Debugging session...")
    import os
    session_id = request.cookies.get("session")  # This is what Flask gets from the browser
    session_files = os.listdir("./flask_sessions/")  # Check stored session files

    return jsonify({
        "session_id_from_cookie": session_id,
        "stored_sessions": session_files,
        "current_session_data": dict(session)
    })


@app.route('/profile', methods=['GET'])
def profile():
    if 'candidate_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    candidate = Candidate.query.get(session['candidate_id'])

    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404

    return jsonify({
        'full_name': candidate.full_name,
        'email': candidate.email,
        'id': candidate.id,
        'message': 'Profile fetched successfully!'
    }), 200


@app.route('/logout')
def logout():
    session.pop('candidate_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = Candidate.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found'}), 400

    reset_token = secrets.token_hex(16)
    user.forgot_password = reset_token
    db.session.commit()

    msg = Message("Password Reset Request", recipients=[email])
    msg.body = f"Your password reset token is: {reset_token}"

    try:
        mail.send(msg)
        return jsonify({'message': 'Reset token sent to email'}), 200
    except Exception as e:
        return jsonify({'error': f"Failed to send email: {str(e)}"}), 500


@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    reset_token = data.get('reset_token')
    new_password = data.get('new_password')

    if not email or not reset_token or not new_password:
        return jsonify({'error': 'Email, reset token, and new password are required'}), 400

    user = Candidate.query.filter_by(email=email, forgot_password=reset_token).first()

    if not user:
        return jsonify({'error': 'Invalid email'}), 400

    hashed_password = generate_password_hash(new_password)
    user.password = hashed_password

    user.forgot_password = None
    db.session.commit()

    return jsonify({'message': 'Password reset successful'}), 200


@app.route('/candidates', methods=['GET'])
def get_candidates():
    candidates = Candidate.query.all()

    candidate_list = []
    for candidate in candidates:
        candidate_list.append({
            'id': candidate.id,
            'full_name': candidate.full_name,
            'email': candidate.email
        })
    return jsonify({'candidates': candidate_list}), 200


@app.route('/candidates/<int:id>', methods=['GET'])
def get_candidate(id):
    user = Candidate.query.get(id)

    if not user:
        return jsonify({'error': 'Candidate not found'}), 404

    return jsonify({
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email
    }), 200


@app.route('/get_name_profile_image/<int:candidate_id>', methods=['GET'])
def get_name_profile_image(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404

    verification = Verification.query.filter_by(candidate_id=candidate_id).first()
    profile_image = verification.profile_image if verification else None

    return jsonify({
        'full_name': candidate.full_name,
        'profileImage': profile_image
    }), 200


@app.route('/get_verifications', methods=['GET'])
def get_all_verifications():
    verifications = Verification.query.all()

    verifications_list = [
        {
            "id": v.id,
            "candidate_id": v.candidate_id,
            "phone_number": v.phone_number,
            "national_id": v.national_id,
            "profile_image": v.profile_image,
            "is_verified": v.is_verified,
            "category": v.category,
            "vote_count": v.vote_count

        }
        for v in verifications
    ]
    return jsonify({"verifications": verifications_list}), 200


# @app.route('/verify_candidate_details', methods=['POST'])
# def verify_candidate_details():
#     data = request.get_json()
#     print("Received data:", data)
#
#     candidate_id = data.get('candidate_id')
#     national_id = data.get('national_id')
#     phone_number = data.get('phone_number')
#
#     if not candidate_id or not national_id or not phone_number:
#         return jsonify({'error': 'All fields (candidate_id, national_id, phone_number) are required'}), 400
#
#
#     candidate  = Candidate.query.get(candidate_id)
#     if not candidate:
#         return jsonify({'error': 'Candidate not found'}), 404
#
#     verification = Verification.query.filter_by(candidate_id=candidate_id).first()
#     if verification:
#         if verification.national_id == national_id and verification.phone_number == phone_number:
#             if verification.is_phone_verified:
#                 verification.is_verified = True
#                 db.session.commit()
#                 return jsonify({'message': 'Candidate verified successfully'}), 200
#             else:
#              return jsonify({'error': 'Phone number not verified yet.'}), 400
#         else:
#           return jsonify({'error': 'Verification failed. National ID and phone number do not match'}), 400
#     else:
#         return jsonify({'error': 'Candidate verification record not found'}), 404


@app.route('/get_candidate_id/<national_id>', methods=['GET'])
def get_candidate_id(national_id):
    candidate = Candidate.query.filter_by(national_id=national_id).first()

    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404

    return jsonify({'candidate_id': candidate.id}), 200


# @app.route('/upload_image/<int:candidate_id>', methods=['POST'])
# def upload_image(candidate_id):
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#
#         verification = Verification.query.filter_by(candidate_id=candidate_id).first()
#
#         if verification:
#             verification.profile_image = filename
#             db.session.commit()
#         else:
#             return jsonify({'error': 'Verification record not found'}), 404
#
#         return jsonify({'message': 'Image uploaded successfully'}), 200
#
#     else:
#         return jsonify({'error': 'Invalid file type'}), 400


@app.route('/verify_and_send_otp', methods=['POST'])
def verify_and_send_otp():
    data = request.get_json()
    print("Received data:", data)

    # candidate_id = data.get('candidate_id')
    national_id = data.get('national_id')
    phone_number = data.get('phone_number')

    if not national_id or not phone_number:
        return jsonify({'error': 'National ID and phone number are required'}), 400

    verification = Verification.query.filter_by(national_id=national_id).first()

    if not verification:
        return jsonify({'error': 'Verification record not found'}), 404

    candidate_id = verification.candidate_id

    if verification.phone_number != phone_number:
        return jsonify({'error': 'Phone number does not match records'}), 400

    if not verification.is_verified:
        return jsonify({'error': 'Phone number not verified yet.'}), 400

    if not phone_number.startswith('+'):
        phone_number = '254' + phone_number.lstrip('0')

    try:
        otp_verification = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID) \
            .verifications.create(to=phone_number, channel='sms')

        return jsonify({
            'message': 'Candidate verified successfully, OTP sent!',
            'otp_status': otp_verification.status,
            'candidate_id': candidate_id
        }), 200

    except Exception as e:
        return jsonify({'error': 'Verification successful, but OTP sending failed: ' + str(e)}), 500


# @app.route('/send_otp', methods=['POST'])
# def send_otp():
#     data = request.get_json()
#     phone_number = data.get('phone_number')
#
#
#     if not phone_number:
#         return jsonify({'error': 'Phone number is required'}), 400
#
#     if not phone_number.startswith('+'):
#         phone_number = '254' + phone_number.lstrip('0')
#
#     try:
#         verification = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID) \
#         .verifications.create(to=phone_number, channel='sms')
#         return jsonify({'message': 'OTP sent successfully!', 'status': verification.status}), 200
#
#     except Exception as e:
#        return jsonify({'error': str(e)}), 500


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone_number = data.get('phone_number')
    otp = data.get('otp')

    if not phone_number or not otp:
        return jsonify({'error': 'Phone number and OTP are required'}), 400

    try:
        verification_check = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID) \
            .verification_checks.create(to=phone_number, code=otp)

        if verification_check.status == "approved":
            verification = Verification.query.filter_by(phone_number=phone_number).first()

            if verification:
                verification.is_verified = True
                db.session.commit()
                return jsonify({'message': 'Phone number verified successfully!'}), 200

            else:
                return jsonify({'error': 'Verification record not found. Please register first.'}), 404

        return jsonify({'error': 'Invalid OTP. Please try again.'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/assign_category', methods=['POST'])
def assign_category():
    if 'candidate_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    candidate_id = session['candidate_id']
    data = request.get_json()
    category = data.get('category')

    print(f"Received data from frontend: {data}")
    print(f"Extracted category: {category}")

    print(f"Received candidate_id: {candidate_id}, category: {category}")

    if not category:
        print("🚨 Category is missing in the request!")
        return jsonify({'error': 'Category is required'}), 400

    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404

    verification = Verification.query.filter_by(candidate_id=candidate_id).first()
    if verification:
        verification.category = category

    else:
        verification = Verification(
            candidate_id=candidate_id,

            # phone_number=None,
            # national_id=None,
            # profile_image=None,
            # is_verified=False,
            # category=category,
            # vote_count=0

        )
        db.session.add(verification)

    db.session.commit()
    return jsonify({'message': 'Category assigned successfully'}), 200


@app.route('/list_candidates', methods=['GET'])
def list_candidates():
    category = request.args.get('category')
    if not category:
        return jsonify({'error': 'Category is required'}), 400

    verifications = Verification.query.filter_by(category=category).all()

    candidates = []
    for verification in verifications:
        candidate = Candidate.query.get(verification.candidate_id)
        if candidate:
            candidates.append({
                'id': candidate.id,
                'full_name': candidate.full_name,
                'email': candidate.email
            })

    return jsonify({'candidates': candidates}), 200


@app.route('/vote', methods=['POST'])
def vote():
    data = request.get_json()
    voter_phone = data.get('voter_phone')
    candidate_id = data.get('candidate_id')

    if not voter_phone or not candidate_id:
        return jsonify({'error': 'Voter phone and candidate ID are required'}), 400

    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404

    verification = Verification.query.filter_by(candidate_id=candidate_id).first()
    if verification:
        verification.vote_count += 1
        db.session.commit()
    else:
        return jsonify({'error': 'Verification record not found'}), 404

    new_vote = Votes(candidate_id=candidate_id, voter_phone=voter_phone)
    db.session.add(new_vote)
    db.session.commit()

    return jsonify({'message': 'Vote recorded successfully'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
