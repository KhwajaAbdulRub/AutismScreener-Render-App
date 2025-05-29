from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import os
from werkzeug.utils import secure_filename
from ai_models import AutismDetectionAI

# Create Flask app instance
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key
login_manager = LoginManager(app)
login_manager.login_view = 'login'

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Dummy user storage (replace with database in production)
users = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id, users.get(int(user_id), {}).get('username', ''))

# Forms
class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class UserInfoForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    ethnicity = StringField('Ethnicity', validators=[DataRequired()])
    submit = SubmitField('Proceed to Assessment')

class FeedbackForm(FlaskForm):
    feedback = TextAreaField('Your Feedback', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Submit Feedback')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about_autism')
def about_autism():
    return render_template('about_autism.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        if any(user['email'] == email for user in users.values()):
            flash('Email already registered.', "danger")
            return redirect(url_for('signup'))
        user_id = len(users) + 1
        users[user_id] = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password)
        }
        flash('Sign-up successful! Please log in.', "success")
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user_id = None
        for uid, user in users.items():
            if user['email'] == email and check_password_hash(user['password'], password):
                user_id = uid
                break
        if user_id:
            user = User(user_id, users[user_id]['username'])
            login_user(user)
            return redirect(url_for('home'))  # Redirect to home instead of user_info
        flash('Invalid email or password.', "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    # Clear session data on logout
    session.pop('user_info', None)
    session.pop('symptoms', None)
    session.pop('images', None)
    session.pop('current_question', None)
    logout_user()
    return redirect(url_for('home'))

@app.route('/user_info_assessment', methods=['GET', 'POST'])
@login_required
def user_info_assessment():
    form = UserInfoForm()
    if form.validate_on_submit():
        session['user_info'] = {
            'age': form.age.data,
            'gender': form.gender.data,
            'ethnicity': form.ethnicity.data
        }
        return redirect(url_for('symptom_question'))
    return render_template('user_info.html', form=form)

@app.route('/symptoms/start')
@login_required
def symptoms_start():
    # Clear previous session data to treat this as a new assessment
    session.pop('user_info', None)
    session.pop('symptoms', None)
    session.pop('images', None)
    session['current_question'] = 0
    session['symptoms'] = {}
    session['images'] = []
    return redirect(url_for('user_info_assessment'))  # Redirect to collect user info

@app.route('/symptom/question', methods=['GET', 'POST'])
@login_required
def symptom_question():
    if 'user_info' not in session:
        return redirect(url_for('user_info_assessment'))
    if 'symptoms' not in session:
        session['symptoms'] = {}
    if 'images' not in session:
        session['images'] = []

    symptoms = [
        {'title': 'Difficulty with Eye Contact', 'description': 'Does the child have trouble looking at others\' eyes during conversations?', 'field': 'eye_contact'},
        {'title': 'Challenges with Social Interaction', 'description': 'Does the child find it hard to start or join social activities with others?', 'field': 'social_interaction'},
        {'title': 'Repetitive Behaviors', 'description': 'Does the child repeat actions like hand-flapping or lining up toys?', 'field': 'repetitive_behavior'},
        {'title': 'Delayed Speech', 'description': 'Is the child\'s speech developing slower than other kids their age?', 'field': 'delayed_speech'},
        {'title': 'Echolalia', 'description': 'Does the child repeat words or phrases they hear, like from TV?', 'field': 'echolalia'},
        {'title': 'Sound Sensitivity', 'description': 'Does the child get upset by loud sounds like vacuums or sirens?', 'field': 'sound_sensitivity'},
        {'title': 'Touch Sensitivity', 'description': 'Does the child dislike certain textures or pull away from hugs?', 'field': 'touch_sensitivity'},
        {'title': 'Difficulty with Emotional Regulation', 'description': 'Does the child have frequent meltdowns or trouble calming down?', 'field': 'emotional_regulation'},
        {'title': 'Resistance to Change', 'description': 'Does the child get upset when routines or plans change?', 'field': 'change_resistance'},
        {'title': 'Aggression', 'description': 'Does the child hit or throw things when frustrated?', 'field': 'aggression'}
    ]

    current_question = session.get('current_question', 0)

    if current_question >= len(symptoms):
        return redirect(url_for('result'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'previous' and current_question > 0:
            session['current_question'] = current_question - 1
            return redirect(url_for('symptom_question'))

        response = request.form.get('response')
        symptom_key = symptoms[current_question]['field']
        session['symptoms'][symptom_key] = response == 'yes'

        # Handle image upload
        image = request.files.get('image_file')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{symptom_key}_{filename}")
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            image.save(image_path)
            absolute_image_path = os.path.abspath(image_path)
            session['images'].append(absolute_image_path)
            print(f"Image uploaded: {absolute_image_path}")

        current_question += 1
        session['current_question'] = current_question

        if current_question >= len(symptoms):
            print("Symptom Dict:", session['symptoms'])
            print("Images in session:", session['images'])
            return redirect(url_for('result'))

    symptom = symptoms[current_question]
    return render_template('symptom_question.html', symptom=symptom, question_number=current_question + 1, total_questions=len(symptoms), field_name=symptom['field'])

@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = form.feedback.data
        with open('feedback.txt', 'a') as f:
            f.write(f"{current_user.id}: {feedback}\n")
        flash('Thank you for your feedback!', "success")
    return redirect(url_for('result'))

@app.route('/result', methods=['GET', 'POST'])
@login_required
def result():
    symptoms = session.get('symptoms', {})
    user_info = session.get('user_info', {})
    images = session.get('images', [])
    ai = AutismDetectionAI()

    print(f"Debug: Symptoms: {symptoms}")
    print(f"Debug: User Info: {user_info}")
    print(f"Debug: Images: {images}")

    image_path = images[-1] if images else None
    print(f"Debug: Image path passed to AI: {image_path}")
    if image_path and not os.path.exists(image_path):
        print(f"Error: Image file does not exist at {image_path}")
        image_path = None

    combined_score, risk_level, symptom_score, image_score, meltdown_prob = ai.get_combined_prediction(symptoms, user_info, image_path)
    print(f"Debug: Combined Score: {combined_score}, Symptom Score: {symptom_score}, Image Score: {image_score}, Meltdown Prob: {meltdown_prob}")

    meltdown_detected = image_path and meltdown_prob > 0.4

    # Scale down the combined score to be less alarming (target 73-80% range)
    if combined_score > 80:
        scaled_combined_score = int(73 + (combined_score - 80) * 0.3)  # Linear scaling
        scaled_combined_score = min(scaled_combined_score, 80)  # Cap at 80%
    else:
        scaled_combined_score = int(combined_score)
    print(f"Debug: Scaled Combined Score: {scaled_combined_score}")

    # Simplified but detailed explanation
    yes_symptoms = [k for k, v in symptoms.items() if v]
    explanation = f"Based on your answers, you noted 'Yes' to: {', '.join(yes_symptoms)}. These behaviors, especially {', '.join(yes_symptoms[-2:] if len(yes_symptoms) > 1 else yes_symptoms)}, suggest a possibility of autism spectrum disorder (ASD) traits. The child’s age ({user_info.get('age', 'not provided')}) and gender ({user_info.get('gender', 'not provided')}) also play a role in this assessment. This is not a diagnosis—please see a professional for confirmation."
    what_to_be_aware = [
        f"Watch for signs like {', '.join(yes_symptoms[:2]) if yes_symptoms else 'social challenges'} that might need attention.",
        "Keep track of milestones like speech or emotional growth—delays could be important.",
        "This score indicates a chance of ASD traits, but only a doctor can give a final answer."
    ]

    form = FeedbackForm()
    if form.validate_on_submit():
        return submit_feedback()

    return render_template('result.html', combined_score=scaled_combined_score, risk_level=risk_level,
                          symptom_score=symptom_score, image_score=int(image_score),
                          meltdown_detected=meltdown_detected, meltdown_prob=meltdown_prob,
                          symptoms=symptoms, user_info=user_info, explanation=explanation,
                          what_to_be_aware=what_to_be_aware, feedback_form=form, yes_symptoms=yes_symptoms, images=images)

if __name__ == '__main__':
    app.run(debug=True)