import pandas as pd
from datetime import datetime
import os

DATA_FILE = "mood_data.csv"

def save_mood(mood, text):
    new_data = pd.DataFrame({
        "time": [datetime.now()],
        "mood": [mood],
        "text": [text]
    })

    if os.path.exists(DATA_FILE):
        old = pd.read_csv(DATA_FILE)
        df = pd.concat([old, new_data], ignore_index=True)
    else:
        df = new_data

    df.to_csv(DATA_FILE, index=False)
