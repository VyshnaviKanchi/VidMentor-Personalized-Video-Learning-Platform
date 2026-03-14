import mysql.connector
import bcrypt

#to conect to the database
def get_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root", # use your database password
        database="Data"
    )
    return conn


#-------------------------------------------------------------------------
# FUNCTIONS NEEDED FOR PUSHING DATA TO TABELS
#-------------------------------------------------------------------------

#to rigister students in the sine up page
def register_student(name, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # check if email already exists
        cursor.execute("SELECT student_id FROM students WHERE email = %s", (email,))
        if cursor.fetchone():
            print("Email already registered")
            return None

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        query = """
        INSERT INTO students (name, email, password)
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (name, email, hashed_password))
        conn.commit()

        return cursor.lastrowid

    except mysql.connector.Error as err:
        print("Error:", err)
        return None

    finally:
        cursor.close()
        conn.close()


#To save the feedback of the user
def save_feedback(student_id, video_id, rating, like_dislike, comment): #front end
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO feedback
        (student_id, video_id, rating, like_dislike, comment)
        VALUES (%s,%s,%s,%s,%s)
        """

        cursor.execute(query, (student_id, video_id, rating, like_dislike, comment))
        conn.commit()
    except mysql.connector.Error as err: #incase any issues come we give this to prevent crashing
        print("Error:", err)
        return None 

    finally:
        cursor.close()
        conn.close()

#to save the filltered videos gotten from the API
def save_videos(subject, difficulty, title, url, duration): #API
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO videos (subject, difficulty, title, url, duration)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (subject, difficulty, title, url, duration))
        conn.commit()

        print("Video saved successfully")

    except mysql.connector.Error as err:
        print("Error:", err)

    finally:
        cursor.close()
        conn.close()

#To save the preference
def save_preferences(student_id, p_class, subjects, difficulty, pace, style):#front end

    conn = get_connection()
    cursor = conn.cursor()

    try:
        subjects_string = ",".join(subjects)

        # Check if preferences already exist
        check_query = """
        SELECT student_id FROM preferences
        WHERE student_id = %s
        """
        cursor.execute(check_query, (student_id,))
        existing = cursor.fetchone()

        if existing:
            # Update existing preferences
            update_query = """
            UPDATE preferences
            SET class_level=%s,
                subjects=%s,
                difficulty=%s,
                pace=%s,
                learning_style=%s
            WHERE student_id=%s
            """
            cursor.execute(update_query,
                (p_class, subjects_string, difficulty, pace, style, student_id)
            )

        else:
            # Insert new preferences
            insert_query = """
            INSERT INTO preferences
            (student_id, class_level, subjects, difficulty, pace, learning_style)
            VALUES (%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(insert_query,
                (student_id, p_class, subjects_string, difficulty, pace, style)
            )

        conn.commit()

    except mysql.connector.Error as err:
        print("Error:", err)

    finally:
        cursor.close()
        conn.close()

#To save the user's hystory
def save_history(student_id, video_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO history (student_id, video_id)
        VALUES (%s, %s)
        """

        cursor.execute(query, (student_id, video_id))
        conn.commit()

        print("History saved")

    except mysql.connector.Error as err:
        print("Database Error:", err)

    finally:
        cursor.close()
        conn.close()

# ALL DONE ---------------------------------------------------------------------------------------------

#--------------------------------------------------------------------
# DATA RETREVEL
#--------------------------------------------------------------------

#to call vodeos that are searched
def get_videos(subject):  # matching algorithm
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT video_id, subject, difficulty, duration, title, url FROM videos
        WHERE subject LIKE %s or title Like %s
        """

        cursor.execute(query, ("%" + subject + "%",))
        videos = cursor.fetchall()

        return videos

    except mysql.connector.Error as err:
        print("Database Error:", err)
        return []

    finally:
        cursor.close()
        conn.close()
# DONE -------------------------------------------------------------------------------------------------

# loging in for the user to work. along with decripting the hashing to get original pasword
def login_student(email, password):# front end
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT student_id, password
        FROM students
        WHERE email = %s
        """

        cursor.execute(query, (email,))
        result = cursor.fetchone()

        if result:
            stored_hash = result["password"]

            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return result["student_id"]

        return None

    except mysql.connector.Error as err:
        print("Database Error:", err)
        return None

    finally:
        cursor.close()
        conn.close()

        #DONE-----------------------------------------------------------------------
    
# to check if user is first time user
def has_feedback(student_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        
        query = """
        SELECT COUNT(*) 
        FROM feedback
        WHERE student_id = %s
        """

        cursor.execute(query, (student_id,))
        count = cursor.fetchone()[0]

        return count > 0

    finally:
        cursor.close()
        conn.close()
# DONE-------------------------------------------------------------------------------------------------


#To get the preferences of the students
# To get the preferences of the students
def get_student_preferences(student_id): # Algorithem
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT student_id, class_level, subjects, difficulty, pace, learning_style
        FROM preferences
        WHERE student_id = %s
        """
        cursor.execute(query, (student_id,))
        
        # FIX: You MUST fetch the result before closing the cursor
        result = cursor.fetchone() 
        return result

    except mysql.connector.Error as err:
        print("Database Error:", err)
        return None

    finally:
        # Now it is safe to close because the result has been read
        cursor.close()
        conn.close()

# DONE ---------------------------------------------------------------------------------------------------------

#gives record of all past interactions 
def get_all_feedback():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT student_id, video_id, rating
    FROM feedback
    """

    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

# DONE----------------------------------------------------------------------------------------

# to get all the viodeos from the videos tabel in the database
def get_all_videos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT video_id, subject, difficulty, duration, title, url
    FROM videos
    """

    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


# To get 
def get_history(student_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT v.video_id, v.title, v.url, h.watched_at
        FROM history h
        JOIN videos v ON h.video_id = v.video_id
        WHERE h.student_id = %s
        ORDER BY h.watched_at DESC
        """

        cursor.execute(query, (student_id,))
        result = cursor.fetchall()

        return result

    except mysql.connector.Error as err:
        print("Database Error:", err)
        return []

    finally:
        cursor.close()
        conn.close()
