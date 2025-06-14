import pickle

# Load the model
with open('mood_model_4.pkl', 'rb') as f:
    model = pickle.load(f)

# Re-save the model
with open('mood_model_4.pkl', 'wb') as f:
    pickle.dump(model, f) 