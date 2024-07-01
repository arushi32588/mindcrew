from models import db, Achievement, Mood

def award_achievement(user_id, name, description):
    achievement = Achievement(user_id=user_id, name=name, description=description)
    db.session.add(achievement)
    db.session.commit()

def check_for_achievements(user_id):
    # Example logic for awarding achievements
    award_first_mood_entry(user_id)
    award_consistent_tracker(user_id)

def award_first_mood_entry(user_id):
    user_achievements = Achievement.query.filter_by(user_id=user_id, name="First Mood Entry").first()
    if not user_achievements:
        award_achievement(user_id, "First Mood Entry", "Logged your first mood entry!")

def award_consistent_tracker(user_id):
    user_moods = Mood.query.filter_by(user_id=user_id).order_by(Mood.date.desc()).limit(7).all()
    if len(user_moods) == 7:
        dates = [mood.date for mood in user_moods]
        if all((dates[i] - dates[i+1]).days == 1 for i in range(6)):
            user_achievements = Achievement.query.filter_by(user_id=user_id, name="Consistent Tracker").first()
            if not user_achievements:
                award_achievement(user_id, "Consistent Tracker", "Logged mood entries for seven consecutive days!")
