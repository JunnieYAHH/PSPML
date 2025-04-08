
import pymongo
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

def logs_prediction():
   # Connect to MongoDB
    client = pymongo.MongoClient('mongodb+srv://gerelitopuyos:gerelitopuyos@atlascluster.7cyczkf.mongodb.net/PSPData?retryWrites=true&w=majority')  # Adjust the URI if necessary
    db = client['PSPData']  # Replace with your database name   
    collection = db['logs']  # Replace with your collection name
    # Fetch the data
    data = list(collection.find())

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Use 'timeIn' for actual login time
    df['date'] = pd.to_datetime(df['timeIn'], errors='coerce')

    # Extract just the date (no time part)
    df['day'] = df['date'].dt.date

    # Group by day and count logins
    daily_counts = df.groupby('day').size().reset_index(name='logins')

    # Convert 'day' back to datetime and sort
    daily_counts['day'] = pd.to_datetime(daily_counts['day'])
    daily_counts.sort_values('day', inplace=True)

    # 🔥 Only keep the last 3 days for training
    recent_counts = daily_counts.tail(3).copy()
    recent_counts['day_num'] = (recent_counts['day'] - recent_counts['day'].min()).dt.days

    # Train the model
    X = recent_counts[['day_num']]
    y = recent_counts['logins']

    model = LinearRegression()
    model.fit(X, y)

    # Predict for the next 3 days
    last_day = recent_counts['day'].iloc[-1]
    last_day_num = recent_counts['day_num'].iloc[-1]
    future_day_nums = [last_day_num + i for i in range(1, 4)]
    predicted_dates = [last_day + timedelta(days=i) for i in range(1, 4)]
    predictions = model.predict(pd.DataFrame(future_day_nums, columns=['day_num']))

    # Prepare the prediction results
    prediction_results = []
    for date, prediction in zip(predicted_dates, predictions):
        prediction_results.append({
            "date": date.strftime('%Y-%m-%d'),
            "predicted_logins": max(int(prediction), 0)  # avoid negative predictions
        })

    return prediction_results
