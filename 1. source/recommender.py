import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from database import (
    get_student_preferences,
    get_all_videos,
    get_all_feedback,
    get_history
)

# ------------------------------------------------
# CONTENT BASED FILTERING
# ------------------------------------------------

def content_based_recommendation(student_id):

    preferences = get_student_preferences(student_id)

    if preferences is None:
        print("No preferences found for student:", student_id)
        return {}

    videos = get_all_videos()
    watch_history = get_history(student_id)

    history_ids = [v["video_id"] for v in watch_history]

    scores = {}

    student_subjects = preferences["subjects"].split(",")

    for video in videos:

        if video["video_id"] in history_ids:
            continue

        score = 0

        if video["subject"] in student_subjects:
            score += 3

        if video["difficulty"] == preferences["difficulty"]:
            score += 2

        duration_str = video["duration"]

        if duration_str:
            parts = duration_str.split(":")

            if len(parts) == 3:  # HH:MM:SS
                hours = int(parts[0])
                minutes = int(parts[1])
                duration = hours * 60 + minutes

            elif len(parts) == 2:  # MM:SS
                duration = int(parts[0])

            else:
                duration = 0
        else:
            duration = 0

        if preferences["pace"] == "Fast" and duration <= 10:
            score += 1

        if preferences["pace"] == "Slow" and duration >= 20:
            score += 1

        scores[video["video_id"]] = score

    return scores


# ------------------------------------------------
# MATRIX FACTORIZATION
# ------------------------------------------------

def matrix_factorization():

    feedback = get_all_feedback()
    videos = get_all_videos()

    if len(feedback) == 0:
        return []

    students = list(set([f["student_id"] for f in feedback]))
    video_ids = [v["video_id"] for v in videos]

    student_index = {s: i for i, s in enumerate(students)}
    video_index = {v: i for i, v in enumerate(video_ids)}

    R = np.zeros((len(students), len(video_ids)))

    for f in feedback:
        i = student_index[f["student_id"]]
        j = video_index[f["video_id"]]
        R[i][j] = f["rating"]

    num_users, num_items = R.shape
    K = 2

    P = np.random.rand(num_users, K)
    Q = np.random.rand(num_items, K).T

    steps = 100
    alpha = 0.002
    beta = 0.02

    for step in range(steps):
        for i in range(num_users):
            for j in range(num_items):

                if R[i][j] > 0:

                    eij = R[i][j] - np.dot(P[i, :], Q[:, j])

                    for k in range(K):
                        P[i][k] += alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                        Q[k][j] += alpha * (2 * eij * P[i][k] - beta * Q[k][j])

    predicted_matrix = np.dot(P, Q)

    results = []

    for i, student in enumerate(students):
        for j, video in enumerate(video_ids):

            results.append({
                "student_id": student,
                "video_id": video,
                "rating": predicted_matrix[i][j]
            })

    return results


# ------------------------------------------------
# RANDOM FOREST
# ------------------------------------------------

def random_forest_prediction():

    feedback = get_all_feedback()
    videos = get_all_videos()

    if len(feedback) == 0:
        return {}

    data = []

    for f in feedback:
        for v in videos:
            if f["video_id"] == v["video_id"]:

                data.append({
                    "student_id": f["student_id"],
                    "video_id": v["video_id"],
                    "subject": v["subject"],
                    "difficulty": v["difficulty"],
                    "duration": v["duration"],
                    "rating": f["rating"]
                })

    df = pd.DataFrame(data)

    df = pd.get_dummies(df, columns=["subject", "difficulty"])

    X = df.drop("rating", axis=1)
    y = df["rating"]

    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)

    predictions = {}

    for v in videos:

        row = {
            "student_id": 0,
            "video_id": v["video_id"],
            "duration": v["duration"]
        }

        row[f"subject_{v['subject']}"] = 1
        row[f"difficulty_{v['difficulty']}"] = 1

        test = pd.DataFrame([row]).fillna(0)
        test = test.reindex(columns=X.columns, fill_value=0)

        pred = model.predict(test)[0]

        predictions[v["video_id"]] = pred

    return predictions


# ------------------------------------------------
# HYBRID RECOMMENDER
# ------------------------------------------------

def recommend(student_id):

    videos = get_all_videos()
    watch_history = get_history(student_id)
    history_ids = [v["video_id"] for v in watch_history]

    content_scores = content_based_recommendation(student_id)
    mf_results = matrix_factorization()
    rf_scores = random_forest_prediction()

    final_scores = []

    for video in videos:

        vid = video["video_id"]

        if vid in history_ids:
            continue

        content_score = content_scores.get(vid, 0)

        mf_score = 0
        for r in mf_results:
            if r["student_id"] == student_id and r["video_id"] == vid:
                mf_score = r["rating"]

        rf_score = rf_scores.get(vid, 0)

        if len(mf_results) == 0 and len(rf_scores) == 0:
            final = content_score
        else:
            final = (content_score * 0.3) + (mf_score * 0.4) + (rf_score * 0.3)

        final_scores.append({
            "video_id": vid,
            "title": video["title"],
            "subject": video["subject"],
            "url": video["url"],
            "score": round(final, 3)
        })

    final_scores.sort(key=lambda x: x["score"], reverse=True)

    return final_scores[:5]


# ------------------------------------------------
# TEST SYSTEM
# ------------------------------------------------

if __name__ == "__main__":

    # RETURNING USER
    print("\n===== RETURNING USER =====")

    returning_user = 1
    recs = recommend(returning_user)

    print("Recommendations for returning user:", returning_user)
    for r in recs:
        print(r)

    # NEW USER
    print("\n===== NEW USER =====")

    new_user = 2
    recs = content_based_recommendation(new_user)

    print("Recommendations for new user:", new_user)

    for vid, score in recs.items():
        print({"video_id": vid, "score": score})