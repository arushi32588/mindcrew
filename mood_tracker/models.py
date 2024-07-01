import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import pickle

MOOD_MAP = {
    "sad": 1,
    "unhappy": 2,
    "neutral": 3,
    "happy": 4,
    "ecstatic": 5
}

def load_mood_data(user_id):
    try:
        data = pd.read_csv(f'mood_data_{user_id}.csv')
        data['mood'] = data['mood'].apply(lambda x: MOOD_MAP.get(x, x))
    except FileNotFoundError:
        data = pd.DataFrame(columns=['date', 'mood'])
    return data

def save_mood_data(data, user_id):
    data.to_csv(f'mood_data_{user_id}.csv', index=False)

def train_mood_model(data, user_id):
    data['date'] = pd.to_datetime(data['date'])
    data['day_of_year'] = data['date'].dt.dayofyear
    X = data[['day_of_year']]
    y = data['mood'].astype(float)  # Ensure all mood values are numeric
    
    if len(X) > 1:  # Ensure there is more than one data point
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
    
        y_pred = model.predict(X_test)
        print('Model RMSE:', mean_squared_error(y_test, y_pred, squared=False))
    
        with open(f'mood_model_{user_id}.pkl', 'wb') as f:
            pickle.dump(model, f)
    else:
        print('Not enough data to train the model.')

def predict_mood(day_of_year, user_id):
    try:
        with open(f'mood_model_{user_id}.pkl', 'rb') as f:
            model = pickle.load(f)
        return model.predict([[day_of_year]])[0]
    except FileNotFoundError:
        return 5  # Default mood prediction if model does not exist
