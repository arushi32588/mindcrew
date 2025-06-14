import os
import re
import requests
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Achievement
from mood_tracker.views import mood_tracker_blueprint
from resources.views import resources_blueprint
from chat_support.views import chat_support_blueprint

# Import and configure Google Gemini
import google.generativeai as genai

genai.configure(api_key='AIzaSyCFoeceKdTmB2WsQgpanU7uCCgGQdKVP4I')
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Register the blueprints
app.register_blueprint(mood_tracker_blueprint, url_prefix='/mood_tracker')
app.register_blueprint(resources_blueprint, url_prefix='/resources')
app.register_blueprint(chat_support_blueprint, url_prefix='/chat_support')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            error = 'Username already exists'
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
    return render_template('register.html', error=error)



@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/achievements')
@login_required
def achievements():
    user_achievements = Achievement.query.filter_by(user_id=current_user.id).all()
    return render_template('achievements.html', achievements=user_achievements)

# New route for the virtual coach with enhanced features
@app.route('/coach', methods=['GET', 'POST'])
@login_required
def coach():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        advice = generate_advice(symptoms)
        return render_template('coach.html', symptoms=symptoms, advice=advice)
    return render_template('coach.html')

@app.route('/meditation', methods=['GET', 'POST'])
@login_required
def meditation():
    advice = generate_content("Provide a guided meditation session to help users relax and focus.")
    return render_template('meditation.html', advice=advice)

@app.route('/cbt', methods=['GET', 'POST'])
@login_required
def cbt():
    advice = generate_content("Provide cognitive behavioral techniques to help users identify and challenge negative thought patterns.")
    return render_template('cbt.html', advice=advice)

@app.route('/journaling', methods=['GET', 'POST'])
@login_required
def journaling():
    if request.method == 'POST':
        entry = request.form.get('entry')
        # Save the journal entry to the database (not implemented in this example)
        advice = generate_content("Explain the benefits of journaling for mental health and provide tips on how to start and maintain a journal.")
        return render_template('journaling.html', entry=entry, advice=advice)
    return render_template('journaling.html')

@app.route('/exercises', methods=['GET', 'POST'])
@login_required
def exercises():
    advice = generate_content("Suggest mental health exercises and challenges to promote positive habits and behaviors.")
    return render_template('exercises.html', advice=advice)

@app.route('/create_music', methods=['GET', 'POST'])
@login_required
def create_music():
    return render_template('create_music.html')

# New route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

def generate_advice(symptoms):
    prompt = f"Provide practical advice and exercises for someone experiencing the following symptoms: {symptoms}. Include guided meditation, cognitive behavioral techniques, journaling, and mental health exercises."
    response = model.generate_content(prompt)
    clean_text = clean_response(response.text)
    return clean_text

def generate_content(prompt):
    response = model.generate_content(prompt)
    clean_text = clean_response(response.text)
    return clean_text

def clean_response(text):
    # Remove markdown characters like *, #, and replace multiple newlines with a single newline
    clean_text = re.sub(r'[*#]', '', text)
    clean_text = re.sub(r'\n+', '\n', clean_text)
    return clean_text

def generate_music(music_style, mood, title, make_instrumental):
    try:
        # Generate lyrics based on the mood
        lyrics_url = os.environ.get("SUNO_API_URL_LYRICS", "http://localhost:3000/api/generate_lyrics")
        lyrics_payload = {"prompt": f"A {mood} {music_style} song titled '{title}'"}
        print(f"Sending lyrics request to {lyrics_url} with payload: {lyrics_payload}")
        lyrics_response = requests.post(lyrics_url, json=lyrics_payload)
        lyrics_response.raise_for_status()
        
        # Check if the response has the expected structure
        response_data = lyrics_response.json()
        if not isinstance(response_data, dict):
            raise ValueError(f"Unexpected response format: {response_data}")
        
        lyrics = response_data.get("text")
        if not lyrics:
            raise ValueError(f"No lyrics found in response: {response_data}")

        # Generate music based on the lyrics
        url = os.environ.get("SUNO_API_URL", "http://localhost:3000/api/custom_generate")
        payload = {
            "prompt": lyrics,
            "tags": music_style,
            "title": title,
            "make_instrumental": make_instrumental,
            "wait_audio": True  # Synchronous mode
        }
        headers = {'Content-Type': 'application/json'}
        
        print(f"Sending music generation request to {url} with payload: {payload}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        response_json = response.json()
        if not isinstance(response_json, list) or not response_json:
            raise ValueError(f"Unexpected music response format: {response_json}")
            
        audio_url = response_json[0].get("audio_url")
        if not audio_url:
            raise ValueError(f"No audio URL found in response: {response_json}")
            
        return audio_url, lyrics
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Response text: {e.response.text}")
        return {"error": f"Failed to generate music: {str(e)}"}, "Error generating lyrics"
    except (ValueError, KeyError) as e:
        print(f"Data processing error: {str(e)}")
        return {"error": f"Error processing response: {str(e)}"}, "Error processing response"
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}, "Error occurred"


if __name__ == '__main__':
    app.run(debug=True)
