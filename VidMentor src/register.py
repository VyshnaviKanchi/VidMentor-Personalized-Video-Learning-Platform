from database import (
    register_student,
    login_student,
    save_preferences,
    get_student_preferences,
    get_videos,
    save_feedback,
    save_history,
    get_history
)
from recommender import recommend
import re
import streamlit as st
#importing all functions

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None#To ensure email format

def valid_password(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    return True
#To make sure pasword is in a acceptable format

if "video_count" not in st.session_state:
    st.session_state.video_count = 0

if "page" not in st.session_state:
    st.session_state.page = "Registration"

if "registered" not in st.session_state:
    st.session_state.registered = False

if "Preference_saved" not in st.session_state:
    st.session_state.Preference_saved = False

st.set_page_config(page_title = "Vidmentor Application", layout = "wide")

#----------------- SIDEBAR -----------------#
st.sidebar.title("Navigation")

if st.session_state.get("registered", False):
    st.sidebar.markdown("___")
    st.sidebar.subheader("User Info")
    st.sidebar.write("Name :", st.session_state.get("name"))
    st.sidebar.write("Email :", st.session_state.get("email"))

    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.session_state.page = "Login"
        st.rerun()

if "page" not in st.session_state:
    st.session_state.page = "Registration"

pages = ["Registration", "Login"]

if st.session_state.get("registered"):
    pages.append("Preferences")

if st.session_state.get("Preference_saved"):
    pages.extend(["Videos", "History"])

if st.session_state.get("video_count",0) >= 3:
    pages.append("Feedback")

page = st.sidebar.radio("Go to", pages, index=pages.index(st.session_state.page)
)
st.session_state.page = page

#------------------1. REGISTRATION PAGE------------------#
if page == "Registration":
    st.title("Registration for Personalized Learning Platform")
    st.write("Welcome! This is the UI for our Project.")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if not valid_email(email):
            st.error("Invalid email format")

        elif not valid_password(password):
            st.error("Password must contain at least 8 characters and a number")

        else:

            student_id = register_student(name, email, password)

            if student_id:
                st.session_state.student_id = student_id
                st.session_state.name = name
                st.session_state.email = email
                st.session_state.registered = True
                st.success("Registration Successful!")
                st.session_state.page = "Preferences"
                st.rerun()
            else:
                st.error("Registration failed.")

#------------------ LOGIN PAGE ------------------#
if page == "Login":
    st.title("Student Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        student_id = login_student(email, password)
        if student_id:
            st.session_state.student_id = student_id
            st.session_state.name = email.split("@")[0]
            st.session_state.email = email
            st.session_state.registered = True

            # CHECK FOR EXISTING PREFERENCES
            existing_prefs = get_student_preferences(student_id)
            if existing_prefs:
                # Load existing data into session state
                st.session_state.p_class = existing_prefs["class_level"]
                st.session_state.subjects = existing_prefs["subjects"].split(",")
                st.session_state.difficulty = existing_prefs["difficulty"]
                st.session_state.pace = existing_prefs["pace"]
                st.session_state.style = existing_prefs["learning_style"]
                st.session_state.Preference_saved = True
                
                st.success("Welcome back! Loading your preferences...")
                st.session_state.page = "Videos"
            else:
                st.session_state.page = "Preferences"
            
            st.rerun()
        else:
            st.error("Invalid email or password")

#------------------2. PREFERENCES PAGE------------------#
if page == "Preferences":

    if not st.session_state.get("registered"):
        st.warning("Please login first.")
        st.stop()

    st.write("Logged in as:", st.session_state.name)
    st.write("Email:", st.session_state.email)

    st.title("Set Your Learning Preferences")
    st.write("Tell us about your learning style and goals.")

    class_options = ["Select your class", "1-10", "11-12", "Undergraduate", "Postgraduate", "Other"]

    p_class = st.selectbox(
        "Class",
        class_options,
        index=class_options.index(st.session_state.get("p_class", "Select your class"))
    )

    subjects = st.multiselect(
        "Domain",
        ["Math", "Science", "Literature", "History", "Computer Science", "Other"],
        default=st.session_state.get("subjects", [])
        )


    difficulty_options = ["Select difficulty", "Easy", "Medium", "Hard"]

    difficulty = st.selectbox(
        "Preferred Difficulty Level",
        difficulty_options,
        index=difficulty_options.index(st.session_state.get("difficulty", "Select difficulty"))
    )


    pace_options = ["Select pace", "Slow", "Normal", "Fast"]

    pace = st.selectbox(
        "Preferred Learning Pace",
        pace_options,
        index=pace_options.index(st.session_state.get("pace", "Select pace"))
    )

    style_options = ["Select style", "Visual", "Conceptual", "Step-by-step"]

    style = st.selectbox(
        "Learning Style",
        style_options,
        index=style_options.index(st.session_state.get("style", "Select style"))
    )

    if st.button("Save Preferences"):

        if (
            p_class == "Select your class"
            or difficulty == "Select difficulty"
            or pace == "Select pace"
            or style == "Select style"
            or len(subjects) == 0
        ):
            st.error("Please complete all preference selections.")
        else:
            save_preferences(
            st.session_state.student_id,
            p_class,
            subjects,
            difficulty,
            pace,
            style
            )
            st.session_state.preferences = {
            "class_level": p_class,
            "subjects": subjects,
            "difficulty": difficulty,
            "pace": pace,
            "learning_style": style
            }
            st.session_state.p_class = p_class
            st.session_state.subjects = subjects
            st.session_state.difficulty = difficulty
            st.session_state.pace = pace
            st.session_state.style = style
            st.session_state.Preference_saved = True
            st.success("Preferences Saved!")
            st.session_state.page = "Videos"
            st.rerun()


#------------------3. VIDEOS PAGE------------------#

if page == "Videos":
    if not st.session_state.get("registered", False):
        st.warning("Please register first to access the videos.")
        st.stop()

    if not st.session_state.get("Preference_saved", False):
        st.warning("Please set your preferences first to access the videos.")
        st.stop()
        
    st.write("Logged in as:", st.session_state.name)
    st.write("Email:", st.session_state.email)

    st.title(f"Welcome, {st.session_state.get('name')}!")

    st.subheader("Recommended for You")
    st.write("Based on your learning style and past activity:")

    recommended_list = recommend(st.session_state.student_id)

    if not recommended_list:
        st.info("Start watching videos to get more personalized recommendations!")
    else:
        for rec in recommended_list:
            st.subheader(rec["title"])
            st.caption(f"Subject: {rec['subject']} | Match Score: {rec['score']}")

            video_id = rec["url"].split("v=")[-1]
            embed_url = f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1&controls=1&fs=0"

            st.components.v1.iframe(embed_url, height=400)

            if st.button("Mark as Watched", key=f"rec_watch_{rec['video_id']}"):

                save_history(
                    st.session_state.student_id,
                    rec["video_id"]
                )
                st.session_state.video_count += 1
                st.success("Video saved to history")

    st.markdown("---")

    st.subheader("Search All Videos")
    topic = st.text_input("Search by topic, subject, or keyword")

    if st.button("Search"):
        if topic == "":
            st.warning("Please enter a topic.")
        else:
            videos = get_videos(topic)
            if len(videos) == 0:
                st.warning("No videos found for this topic.")
            for video in videos:
                st.subheader(video["title"])
                st.video(video["url"])
                if st.button("Mark as Watched", key=f"watch_{video['video_id']}"):
                    st.session_state.video_id = video["video_id"]
                    st.session_state.video_count += 1

                    save_history(
                        st.session_state.student_id,
                        video["video_id"]
                    )
                    st.success("Video marked as watched")

                    if st.session_state.video_count >= 3:
                        st.warning("We would love your feedback!")
                        st.session_state.page = "Feedback"
                        st.rerun()

#------------------ HISTORY PAGE ------------------#
elif page == "History":

    
    if not st.session_state.get("registered", False):   
        st.warning("Please login first.")
        st.stop()

    st.title("Watch History")

    videos = get_history(st.session_state.student_id)

    if len(videos) == 0:
        st.info("No videos watched yet.")

    for video in videos:
        st.subheader(video["title"])
        st.video(video["url"])

#------------------4. FEEDBACK PAGE------------------#
elif page == "Feedback":

    if "video_id" not in st.session_state:
        st.warning("Please watch a video before giving feedback.")
        st.stop()

    if not st.session_state.get("Preference_saved", False):
        st.warning("Please set your preferences first.")
        st.stop()

    st.title("Feedback")

    rating = st.slider("Rate the recommendation", 1, 5)
    like_dislike = st.radio("Did you like it?", ["Like", "Dislike"])
    comment = st.text_area("Any suggestions?")

    if st.button("Submit Feedback"):

        save_feedback(
            st.session_state.student_id,
            st.session_state.video_id,
            rating,
            like_dislike,
            comment
        )

        st.session_state.video_count = 0
        st.success("Thank you for your Feedback!")

        st.session_state.page = "Videos"
        st.rerun()
