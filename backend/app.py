from flask import Flask, request, jsonify 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://van:1234@localhost/voting_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app,db)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    forgot_password = db.Column(db.String(255), nullable=True)


class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
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
def sign_up():
    data = request.jsonify()

    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')


    if not full_name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400


    existing_user = Candidate.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 409
    
    new_candidate = Candidate(full_name=full_name, email=email, password=password)

    db.session.add(new_candidate)
    db.session.commit()


    return jsonify({'message': 'Signup successful!'}), 201



if __name__ == '__main__':
    app.run(debug=True)