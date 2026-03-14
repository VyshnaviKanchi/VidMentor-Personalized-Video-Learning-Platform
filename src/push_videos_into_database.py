import pandas as pd
from database import save_videos

# Load dataset
df = pd.read_csv("videos.csv")

for index, row in df.iterrows():

    subject = row["Subject"]
    difficulty = row["Difficulty"]
    title = row["Title"]
    url = row["URL"]
    duration = row["Duration"]

    save_videos(subject, difficulty, title, url, duration)

print("All videos inserted successfully")