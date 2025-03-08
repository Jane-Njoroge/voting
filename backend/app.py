from flask import Flask, request, jsonify 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv




app = Flask(__name__)
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://van:1234@localhost/voting_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS','False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

db = SQLAlchemy(app)
migrate = Migrate(app,db)
mail = Mail(app)


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
        return jsonify({'error': 'Email already registered'}), 409
    ##navigate('/')

    
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

@app.route('/update_candidate/<int:id>', methods=['PUT'])
def update_candidate(id):
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


@app.route('/candidates/<int:candidate_id>', methods=['DELETE'])
def delete_candidate(candidate_id):
    user = Candidate.query.get(candidate_id)

    if not user:
        return jsonify({'error': 'Candidate not found'}), 404


    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Candidate deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)