from googleapiclient.discovery import build
import csv
import re

# Convert YouTube ISO duration to readable format
def convert_duration(iso_duration):
    hours = minutes = seconds = 0

    h = re.search(r'(\d+)H', iso_duration)
    m = re.search(r'(\d+)M', iso_duration)
    s = re.search(r'(\d+)S', iso_duration)

    if h:
        hours = int(h.group(1))
    if m:
        minutes = int(m.group(1))
    if s:
        seconds = int(s.group(1))

    if hours > 0:
        return f"{hours}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes}:{seconds:02}"


API_KEY = "AIzaSyDuaj9PcZ_vKMEtdMvDZFaze7d8m5lBxV8"

youtube = build("youtube", "v3", developerKey=API_KEY)

topics = [
    "Python programming",
    "Java programming",
    "Web development",
    "Artificial Intelligence",
    "Data Science",
    "Machine Learning",
    "Cyber Security",
    "Mathematics",
    "Algebra",
    "Calculus",
    "Statistics",
    "Physics",
    "Chemistry",
    "Biology",
    "History",
    "World History",
    "Ancient History",
    "Economics",
    "Finance",
    "Digital Marketing"
]

all_videos = []

for topic in topics:

    search_request = youtube.search().list(
        part="snippet",
        q=topic,
        type="video",
        maxResults=5
    )

    search_response = search_request.execute()

    for item in search_response["items"]:

        title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]

        url = f"https://www.youtube.com/watch?v={video_id}"

        video_request = youtube.videos().list(
            part="contentDetails",
            id=video_id
        )

        video_response = video_request.execute()

        duration_iso = video_response["items"][0]["contentDetails"]["duration"]
        duration = convert_duration(duration_iso)

        # Difficulty detection
        title_lower = title.lower()

        if any(word in title_lower for word in ["beginner", "beginners", "basics", "intro", "introduction"]):
            difficulty = "Beginner"

        elif any(word in title_lower for word in ["advanced", "expert", "masterclass"]):
            difficulty = "Advanced"

        else:
            difficulty = "mi"

        all_videos.append([topic, difficulty, title, url, duration])


with open("videos.csv", "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow(["Subject", "Difficulty", "Title", "URL", "Duration"])

    writer.writerows(all_videos)

print("Created videos.csv files")