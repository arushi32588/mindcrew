# MindCrew

A comprehensive web application designed to support mental health through various interactive features, mood tracking, and AI-powered assistance.

## Features

### 1. Mood Tracking
- Track daily mood and emotional states
- View mood trends and patterns over time
- Get personalized recommendations based on mood history

### 2. Virtual Mental Health Coach
- AI-powered coaching sessions
- Personalized mental health advice
- Interactive exercises and techniques
- Cognitive Behavioral Therapy (CBT) tools

### 3. Chat Support
- Real-time chat interface
- AI-powered responses to mental health queries
- Empathetic and supportive conversation
- Resource recommendations

### 4. Resources
- Curated mental health resources
- Educational materials
- Self-help guides
- Crisis support information

### 5. Achievements System
- Track progress and milestones
- Gamified experience
- Motivation through achievements
- Progress visualization

## Technical Stack

### Backend
- Python 3.x
- Flask (Web Framework)
- SQLAlchemy (ORM)
- Flask-Login (Authentication)
- Google Gemini API (AI Integration)

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 4.5
- Font Awesome (Icons)
- Google Fonts

### Database
- SQLite (Development)
- SQLAlchemy ORM

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mindcrew.git
cd mindcrew
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the application:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

## Project Structure

```
mindcrew/
├── app.py                 # Main application file
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── instance/            # Instance-specific files
├── static/             # Static files (CSS, JS, images)
├── templates/          # HTML templates
│   ├── base.html      # Base template
│   ├── dashboard.html # Dashboard template
│   └── ...
├── mood_tracker/      # Mood tracking module
├── resources/         # Resources module
└── chat_support/      # Chat support module
```

## Usage

1. **Registration/Login**
   - Create a new account or log in to existing account
   - Secure authentication system

2. **Dashboard**
   - Access all features from the main dashboard
   - Quick navigation to different modules

3. **Mood Tracking**
   - Log daily moods
   - View mood history and trends
   - Get personalized recommendations

4. **Virtual Coach**
   - Start a coaching session
   - Get personalized advice
   - Access CBT exercises

5. **Chat Support**
   - Start a conversation
   - Get AI-powered responses
   - Access resources and support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Security

- Secure password handling
- Protected routes
- Input validation
- XSS protection
- CSRF protection

## Future Enhancements

- Mobile application
- Additional AI models
- Enhanced analytics
- Community features
- Integration with health devices

## Acknowledgments

- Google Gemini API for AI capabilities
- Flask community for the web framework
- All contributors and users of the application 
