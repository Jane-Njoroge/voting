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
CORS(app,supports_credentials=True) 



UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), 'uploads/profile_folder'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://van:1234@localhost/voting_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS','False').lower() == 'true'


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app,supports_credentials=True, origins=["http://127.0.0.1:5500", "http://localhost:3000"]) 

db = SQLAlchemy(app)
migrate = Migrate(app,db)
mail = Mail(app)




app.config['DEBUG'] = True
logging.basicConfig(level=logging.DEBUG)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config["SESSION_COOKIE_SECURE"] = True




app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)



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
    phone_number = db.Column(db.String(20),unique=True, nullable=False)
    national_id = db.Column(db.String(50), unique=True,nullable=False)
    profile_image = db.Column(db.String(255), nullable=True, default='default.jpg') 
    is_verified = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(200), nullable=False, default='Uncategorized') 
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

    session_id = request.cookies.get("session")  # This is what Flask gets from the browser
    session_files = os.listdir("./flask_sessions/")  # Check stored session files

    return {
        "session_id_from_cookie": session_id,
        "stored_sessions": session_files,
        "current_session_data": dict(session)
    }





@app.route("/check-session")
def check_session():
    print("Session Data:", session)
    if "user_id" in session:
        return jsonify({"message": "Session Active", "user_id": session["user_id"]})
    return jsonify({"error": "No Active Session"}), 401



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


@app.route('/login',methods=['POST'])
def login():
    print("🚀 LOGIN ROUTE HIT!")

    data = request.get_json()
    print("Received login data:", data)

    email = data.get('email')
    password = data.get('password')


    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = Candidate.query.filter_by(email=email).first()
    print("Queried user:", user)

    if not user:
        
        return jsonify({'error': 'Invalid email or password'}), 401
    

    if not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    candidate_id = user.id
    print("Candidate ID being sent:", candidate_id)


    
    session['candidate_id'] = user.id
    session.modified = True

    

    
    return jsonify({'message': 'Login successful!','candidate_id': user.id}), 200




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





@app.route('/get_name_profile_image/<int:candidate_id>', methods=['GET'])
def get_name_profile_image(candidate_id):
     candidate = Candidate.query.get(candidate_id)
     if not candidate:
         return jsonify({'error': 'Candidate not found'}), 404
     
     verification = Verification.query.filter_by(candidate_id=candidate_id).first()
     profile_image = verification.profile_image if verification else None

     return jsonify({
         'full_name':candidate.full_name,
         'profileImage':profile_image
     }),200


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





#@app.route('/verify_candidate_details', methods=['POST'])
#def verify_candidate_details():
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
    

@app.route('/get_candidate_id/<national_id>', methods=['GET'])
def get_candidate_id(national_id):
    candidate = Candidate.query.filter_by(national_id=national_id).first()
    
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404

    return jsonify({'candidate_id': candidate.id}), 200 







@app.route('/verify_and_send_otp', methods=['POST'])

def verify_and_send_otp():
    data = request.get_json()
    print("Received data:", data)

    #candidate_id = data.get('candidate_id')
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





#@app.route('/send_otp', methods=['POST'])
#def send_otp():
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
            
             #phone_number=None,
             #national_id=None,
             #profile_image=None,
             #is_verified=False,
             #category=category,
             #vote_count=0 

         )
         db.session.add(verification)

    db.session.commit()
    return jsonify({'message': 'Category assigned successfully'}), 200




#@app.route('/assign_category', methods=['POST'])
#def assign_category():
    if 'candidate_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    candidate_id = int(session['candidate_id'])  # 🔥 Ensure it's an integer
    data = request.get_json()
    category = data.get('category')

    print(f"Received candidate_id: {candidate_id}, category: {category}")

    if not category:
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
            phone_number=None,
            national_id=None,
            profile_image=None,
            is_verified=False,
            category=category,
            vote_count=0
        )
        db.session.add(verification)

    # 🔥 Debugging SQL Issues
    try:
        print(f"SQL Debug: Candidate ID={candidate_id}, Category={category}")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("🔥 Error committing to database:", str(e))
       # traceback.print_exc()  # Show full error
        return jsonify({'error': 'Internal Server Error'}), 500

    return jsonify({'message': 'Category assigned successfully'}), 200


        

@app.route('/verify_candidate', methods=['POST'])
def verify_candidate():
    data = request.get_json()
    candidate_id = data.get('candidate_id')

    print(f"Received candidate_id: {candidate_id}")

    if not candidate_id:
        return jsonify({'error': 'Candidate ID is required'}), 400

    # Check if candidate exists
    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404

    # Check if verification already exists
    verification = Verification.query.filter_by(candidate_id=candidate_id).first()
    if verification:
        return jsonify({'error': 'Candidate is already verified'}), 400

    # Create new verification record
    new_verification = Verification(
        candidate_id=candidate_id,
        phone_number=data.get('phone_number'),
        national_id=data.get('national_id'),
        profile_image=data.get('profile_image'),
        is_verified=False,
        category=data.get('category')
    )

    db.session.add(new_verification)
    db.session.commit()

    return jsonify({'message': 'Verification record created successfully'}), 200



@app.route('/fetch_category/<int:candidate_id>', methods=['GET'])
def fetch_category(candidate_id):
    try:
        
        verifications = Verification.query.filter_by(candidate_id=candidate_id).all()

        if not verifications:
            return jsonify({"error": "No verifications found for this candidate"}), 404

    
        categories = list(set([verification.category for verification in verifications]))

    
        candidate = Candidate.query.get(candidate_id)
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

    
        candidate_data = {"id": candidate.id, "name": candidate.full_name}

        return jsonify({"categories": categories, "candidate": candidate_data}), 200

    except Exception as e:
        print(f"Error: {e}") 
        return jsonify({"error": str(e)}), 500


    


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
        
        relative_path = f"profile_folder/{filename}"
        candidate.profile_image = relative_path
        db.session.commit()

        return jsonify({'message': 'Profile image uploaded successfully', 'image_url': f"/uploads/{relative_path}"}), 200
    
    return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400



@app.route('/vote', methods=['POST'])
def vote():
    try:
        # Get the voter phone and candidate ID from the request body
        voter_phone = request.json.get('voter_phone')
        candidate_id = request.json.get('candidate_id')
        category = request.json.get('category')  # Assuming category is passed as well
        
        # Check if the candidate exists
        candidate = Candidate.query.get(candidate_id)
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404

        # Find the corresponding verification record for the candidate and category
        verification = Verification.query.filter_by(candidate_id=candidate.id, category=category).first()
        if not verification:
            return jsonify({'error': 'Verification not found for this candidate and category'}), 404

        # Create a new vote entry
        new_vote = Votes(candidate_id=candidate.id, voter_phone=voter_phone)

        # Add the vote to the database
        db.session.add(new_vote)

        # Update the vote count for the verification record
        verification.vote_count += 1
        db.session.commit()

        return jsonify({'message': 'Vote recorded successfully', 'vote_count': verification.vote_count}), 200

    except Exception as e:
        # Return an error if something goes wrong
        return jsonify({'error': str(e)}), 500





@app.route('/delete_unverified_candidates', methods=['DELETE'])
def delete_unverified_candidates():

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




@app.route('/list_candidates', methods=['GET'])
def list_candidates():
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



if __name__ == '__main__':
    app.run(debug=True)