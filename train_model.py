import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from data_extraction import extract_data
from feature_engineering import feature_engineering

def train_model():
    # Extract data
    results_data, driver_standings_data, constructor_standings_data, circuits_data = extract_data()
    
    # Perform feature engineering
    race_features = feature_engineering(results_data, driver_standings_data, constructor_standings_data, circuits_data)
    
    # Define features and target
    X = race_features[['constructorId', 'circuitId', 'points']]
    y = race_features['positionOrder']
    
    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Predict and evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy}")
    
    # Save the model if needed
    pd.to_pickle(model, "race_prediction_model.pkl")

if __name__ == "__main__":
    train_model()
