from flask import Blueprint, request, jsonify, render_template, session
from flask_login import login_required, current_user
from .models import load_mood_data, save_mood_data, train_mood_model, predict_mood
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from models import db, Achievement, Mood, Recommendation
from achievements import check_for_achievements

# Use the Agg backend for Matplotlib
plt.switch_backend('Agg')

mood_tracker_blueprint = Blueprint('mood_tracker', __name__)

MOOD_MAP = {
    "sad": 1,
    "unhappy": 2,
    "neutral": 3,
    "happy": 4,
    "ecstatic": 5
}

@mood_tracker_blueprint.route('/')
@login_required
def index():
    return render_template('mood_tracker.html', descriptions=get_mood_descriptions())

@mood_tracker_blueprint.route('/add', methods=['POST'])
@login_required
def add_mood():
    user_id = current_user.id
    data = load_mood_data(user_id)
    mood_value = MOOD_MAP.get(request.json['mood'], request.json['mood'])
    new_entry = pd.DataFrame([{
        'date': request.json['date'],
        'mood': mood_value
    }])
    data = pd.concat([data, new_entry], ignore_index=True)
    save_mood_data(data, user_id)
    train_mood_model(data, user_id)
    
    # Save new mood entry to the database
    mood_entry = Mood(user_id=user_id, date=pd.to_datetime(request.json['date']), mood=mood_value)
    db.session.add(mood_entry)
    db.session.commit()
    
    check_for_achievements(user_id)
    return jsonify({'message': 'Mood added successfully!'}), 200

@mood_tracker_blueprint.route('/view', methods=['GET'])
@login_required
def view_moods():
    user_id = current_user.id
    data = load_mood_data(user_id)
    return data.to_json(orient='records'), 200

@mood_tracker_blueprint.route('/trend', methods=['GET'])
@login_required
def trend():
    user_id = current_user.id
    data = load_mood_data(user_id)
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values('date')

    dates = data['date'].dt.strftime('%Y-%m-%d').tolist()
    moods = data['mood'].tolist()

    return jsonify({'dates': dates, 'moods': moods})

@mood_tracker_blueprint.route('/recommendations', methods=['GET'])
@login_required
def recommendations():
    user_id = current_user.id
    data = load_mood_data(user_id)
    data['date'] = pd.to_datetime(data['date'])
    today = pd.Timestamp('today').day_of_year
    predicted_mood = predict_mood(today, user_id)
    
    print(f"Predicted Mood: {predicted_mood}")  # Debug statement
    
    recommendations = get_recommendations(predicted_mood)
    print(f"Recommendations: {recommendations}")  # Debug statement
    
    return render_template('recommendations.html', recommendations=recommendations)

def get_recommendations(mood):
    recommendations = []
    if mood < 4:
        recommendations.extend([
            "Consider reaching out to a friend or family member.",
            "Try a relaxation exercise.",
            "Listen to your favorite music."
        ])
    elif mood < 7:
        recommendations.extend([
            "Keep up the good work! How about a short walk?",
            "Try a new hobby or activity.",
            "Spend time with loved ones."
        ])
    else:
        recommendations.extend([
            "You're doing great! Continue with activities that make you happy.",
            "Share your positivity with others.",
            "Plan a fun activity or outing."
        ])
    return recommendations

@mood_tracker_blueprint.route('/analytics')
@login_required
def analytics():
    user_id = current_user.id
    data = load_mood_data(user_id)
    data['date'] = pd.to_datetime(data['date'])
    mood_trend_url = generate_mood_trend_plot(data)
    mood_distribution_url = generate_mood_distribution_plot(data)
    return render_template('analytics.html', mood_trend_url=mood_trend_url, mood_distribution_url=mood_distribution_url)

def generate_mood_trend_plot(data):
    plt.figure(figsize=(10, 5))
    plt.plot(data['date'], data['mood'], marker='o')
    plt.title('Mood Trend Over Time')
    plt.xlabel('Date')
    plt.ylabel('Mood')
    plt.grid(True)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

def generate_mood_distribution_plot(data):
    plt.figure(figsize=(10, 5))
    data['mood'].value_counts().sort_index().plot(kind='bar')
    plt.title('Mood Distribution')
    plt.xlabel('Mood')
    plt.ylabel('Frequency')
    plt.grid(True)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

def get_mood_descriptions():
    return [
        "1 - Extremely Negative Mood (e.g., feeling very depressed, hopeless)",
        "2 - Very Negative Mood (e.g., feeling very sad, anxious)",
        "3 - Negative Mood (e.g., feeling down, unhappy)",
        "4 - Somewhat Negative Mood (e.g., feeling a bit sad, uneasy)",
        "5 - Neutral Mood (e.g., feeling neither happy nor sad, average)",
        "6 - Slightly Positive Mood (e.g., feeling a bit good, content)",
        "7 - Positive Mood (e.g., feeling happy, satisfied)",
        "8 - Very Positive Mood (e.g., feeling very happy, joyful)",
        "9 - Extremely Positive Mood (e.g., feeling extremely happy, delighted)",
        "10 - Euphoric Mood (e.g., feeling ecstatic, elated)"
    ]
