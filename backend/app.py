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




app = Flask(__name__)
load_dotenv()
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), 'uploads/profile_folder'))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://van:1234@localhost/voting_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS','False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

db = SQLAlchemy(app)
migrate = Migrate(app,db)
mail = Mail(app)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



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
    national_id = db.Column(db.String(50), unique=True,nullable=False)
    profile_image = db.Column(db.String(255), nullable=True) 
    is_verified = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), nullable=False) 
    vote_count = db.Column(db.Integer, default=0)


class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    voter_phone = db.Column(db.String(20), nullable=False)




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
        return redirect(url_for('login'))
    
    hashed_password = generate_password_hash(password)
    
    new_candidate = Candidate(full_name=full_name, email=email, password=hashed_password)


    db.session.add(new_candidate)
    db.session.commit()


    return jsonify({'message': 'Signup successful!'}), 201



@app.route('/login',methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')


    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = Candidate.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    

    if not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    return jsonify({'message': 'Login successful!'}), 200




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


    msg  = Message("password Reset Request",
                   recipients=[email])
    
    msg.body = f"Your password reset token is: {reset_token}"

    mail.send(msg)


    return jsonify({'message': 'Reset token sent to email'}), 200


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
            'id':candidate.id,
            'full_name':candidate.full_name,
            'email':candidate.email
        })
    return jsonify({'candidates': candidate_list}), 200 



@app.route('/candidates/<int:id>', methods=['GET'])
def get_candidate(id):
    user = Candidate.query.get(id)


    if not user:
        return jsonify({'error': 'Candidate not found'}), 404
    
    return jsonify({
        'id':user.id,
        'full_name':user.full_name,
        'email':user.email
    }),200

##@app.route('/update_candidate/<int:id>', methods=['PUT'])
##def update_candidate(id):
    data = request.get_json()
    user = Candidate.query.get(id)

    if not user:
        return jsonify({'error': 'Candidate not found'}), 404
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'email' in data:
        user.email = data['email']

    db.session.commit()

    return jsonify({
        'id':user.id,
        'full_name':user.full_name,
        'email':user.email
    }),200


##@app.route('/delete_candidate/<int:candidate_id>', methods=['DELETE'])
##def delete_candidate(candidate_id):
    user = Candidate.query.get(candidate_id)

    if not user:
        return jsonify({'error': 'Candidate not found'}), 404


    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Candidate deleted successfully'}), 200


@app.route('/get_verifications', methods=['GET'])
def get_all_verifications():
    verifications = Verification.query.all()

    verifications_list = [
        {
            "id":v.id,
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





@app.route('/verify_candidate_details', methods=['POST'])
def verify_candidate_details():
    data = request.get_json()
    print("Received data:", data)

    candidate_id = data.get('candidate_id')
    national_id = data.get('national_id')
    phone_number = data.get('phone_number')

    if not candidate_id or not national_id or not phone_number:
        return jsonify({'error': 'All fields (candidate_id, national_id, phone_number) are required'}), 400
    

    candidate  = Candidate.query.get(candidate_id)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    verification = Verification.query.filter_by(candidate_id=candidate_id).first()
    if verification:
        if verification.national_id == national_id and verification.phone_number == phone_number:
            if verification.is_phone_verified:
                verification.is_verified = True
                db.session.commit()
                return jsonify({'message': 'Candidate verified successfully'}), 200
            else:
             return jsonify({'error': 'Phone number not verified yet.'}), 400
        else:
          return jsonify({'error': 'Verification failed. National ID and phone number do not match'}), 400
    else:
        return jsonify({'error': 'Candidate verification record not found'}), 404     
    






@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone_number = data.get('phone_number')


    if not phone_number:
        return jsonify({'error': 'Phone number is required'}), 400
    
    if not phone_number.startswith('+'):
        phone_number = '254' + phone_number.lstrip('0')
    
    try:
        verification = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID) \
        .verifications.create(to=phone_number, channel='sms')
        return jsonify({'message': 'OTP sent successfully!', 'status': verification.status}), 200
    
    except Exception as e:
       return jsonify({'error': str(e)}), 500 






@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data  = request.get_json()
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
                verification.is_phone_verified = True
                db.session.commit()
                return jsonify({'message': 'Phone number verified successfully!'}), 200 
        
            else:
                return jsonify({'error': 'Verification record not found. Please register first.'}), 404


        return jsonify({'error': 'Invalid OTP. Please try again.'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        







@app.route('/verify_candidate', methods=['POST'])
def verify_candidate():
    data = request.get_json()
    candidate_id = data.get('candidate_id')
    profile_image = data.get('profile_image')
    category = data.get('category')
    vote_count = data.get(vote_count)

    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    

    verification = Verification.query.filter_by(candidate_id=candidate_id).first()

    if not verification:
         return jsonify({'error': 'Candidate verification record not found'}), 404
    
    verification.profile_image = profile_image
    verification.category = category
    verification.is_verified = True
    verification.vote_count = 0

    db.session.commit()
    return jsonify({'message': 'Candidate verified successfully'}), 200
    
    
    

@app.route('/get_single_verification/<int:verification_id>',methods=['GET'])
def get_single_verification(verification_id):
    verification = Verification.query.get(verification_id)

    if not verification:
        return jsonify({'error': 'Verification not found'}), 404

    verification_data = {
        "id": verification.id,
         "candidate_id": verification.candidate_id,
         "phone_number": verification.phone_number,
         "national_id": verification.national_id,
         "profile_image": request.host_url + 'uploads/profile_folder/' + verification.profile_image.split('/')[-1] if verification.profile_image else None,
         "is_verified": verification.is_verified,
         "category": verification.category,
         "vote_count": verification.vote_count
    }
    return jsonify(verification_data), 200


@app.route('/verification_status/<int:verification_id>', methods=['PUT'])
def update_verification_status(verification_id):

    data = request.get_json()


    verification = Verification.query.get(verification_id)


    if not verification:
        return jsonify({'error': 'Verification record not found'}), 404


    if 'is_verified' not in data:
        return jsonify({'error': '"is_verified" field is required'}), 400

    verification.is_verified = data['is_verified']
    db.session.commit()


    return jsonify({'message': 'Verification status updated successfully'}), 200






@app.route('/upload_profile_image', methods=['POST'])
def upload_profile_image():
    print(" All Request Files:", request.files.keys())
    print("Request Form:", request.form)

    if 'profile_image' not in request.files:
        return jsonify({'error': 'No image part in request'}), 400
    

    file = request.files['profile_image']
    candidate_id = request.form.get('candidate_id')

    if not candidate_id:
        return jsonify({'error': 'Candidate ID is required'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(file_path)

        candidate = Candidate.query.get(candidate_id)

        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        candidate.profile_image = file_path
        db.session.commit()

        return jsonify({'message': 'Profile image uploaded successfully', 'image_url': file_path}), 200
    
    return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400


#@app.route('/get_profile_image/<filename>', methods=['GET'])
##def get_profile_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/vote',methods=['POST'])
def vote():
    data = request.get_json()
    voter_phone = data.get('voter_phone')
    candidate_id = data.get('candidate_id')


    if not voter_phone or not candidate_id:
        return jsonify({'error': 'Candidate ID and voter phone are required'}), 400
    

    candidate = Candidate.query.get(candidate_id)

    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    

    existing_vote = Votes.query.filter_by(voter_phone=voter_phone).first()
    if existing_vote:
        return jsonify({'error': 'This phone number has already voted'}), 403
    
    new_vote = Votes(candidate_id=candidate_id, voter_phone=voter_phone)
    db.session.add(new_vote)

    verification = Verification.query.filter_by(candidate_id=candidate_id).first()
    if verification:
        verification.vote_count += 1

    db.session.commit()

    return jsonify({
        'message': 'Vote cast successfully!',
        'candidate_id': candidate_id,
        'updated_vote_count': verification.vote_count if verification else "Not tracked"
    }),200





  

##@app.route('/delete_unverified_candidates', methods=['DELETE'])
##def delete_unverified_candidates():

    unverified_candidates = Verification.query.filter(
       (Verification.phone_number == None) | (Verification.phone_number == '') |
        (Verification.national_id == None) | (Verification.national_id == '')
    ).all()


    if not unverified_candidates:
        return jsonify({"message": "No unverified candidates found"}), 200
    
    for candidate in unverified_candidates:
        db.session.delete(candidate)

    db.session.commit()

    return jsonify({"message": "Unverified candidates deleted successfully"}), 200




##@app.route('/list_candidates', methods=['GET'])
##def list_candidates():
    candidates = Candidate.query.all()
    
    if not candidates:
        return jsonify({'message': 'No candidates found in the database'}), 200

    candidates_list = []
    for candidate in candidates:
        verification = Verification.query.filter_by(candidate_id=candidate.id).first()
        candidates_list.append({
            'id': candidate.id,
            'phone_number': verification.phone_number if verification else 'Not available',
            'national_id': verification.national_id if verification else 'Not available',
            'profile_image': verification.profile_image if verification else 'Not available',
            'category': verification.category if verification else 'Not available'
        })
    
    return jsonify({'candidates': candidates_list}), 200


##from sqlalchemy import text

##@app.route('/delete_all_candidates', methods=['DELETE'])
##def delete_all_candidates():
    try:
        # First, delete all verification records
        db.session.execute(text("DELETE FROM verification"))
        
        # Then, delete all candidates
        db.session.execute(text("DELETE FROM candidate"))
        
        db.session.commit()
        return jsonify({'message': 'All candidates deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete candidates', 'details': str(e)}), 500





if __name__ == '__main__':
    app.run(debug=True)