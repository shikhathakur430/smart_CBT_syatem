import streamlit as st
import sqlite3
import pandas as pd
import time
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# -------------------- BASIC SETTINGS --------------------
st.set_page_config(page_title="Smart CBT Examination System", page_icon="📝", layout="wide")
DB_NAME = "cbt_results.db"
EXAM_DURATION = 5  # minutes; change this value to set another duration

QUESTIONS = [
    {
        "question": "Which language is mainly used for this project?",
        "options": ["Java", "Python", "C++", "HTML"],
        "answer": "Python"
    },
    {
        "question": "Which keyword is used to define a function in Python?",
        "options": ["function", "define", "def", "fun"],
        "answer": "def"
    },
    {
        "question": "Which data type stores True or False?",
        "options": ["int", "str", "bool", "list"],
        "answer": "bool"
    },
    {
        "question": "Which symbol is used for comments in Python?",
        "options": ["//", "#", "/*", "<!--"],
        "answer": "#"
    },
    {
        "question": "Which function displays output in Python?",
        "options": ["input()", "show()", "print()", "display()"],
        "answer": "print()"
    },
    {
        "question": "Which collection stores items in key-value pairs?",
        "options": ["List", "Tuple", "Dictionary", "Set"],
        "answer": "Dictionary"
    },
    {
        "question": "Which loop is commonly used to go through a list?",
        "options": ["for", "switch", "repeat", "case"],
        "answer": "for"
    },
    {
        "question": "Which library is used to work with tables of data?",
        "options": ["Pandas", "Turtle", "Random", "Math"],
        "answer": "Pandas"
    },
    {
        "question": "What does SQL stand for?",
        "options": [
            "Structured Query Language",
            "Simple Question Language",
            "System Quick Language",
            "Standard Queue Logic"
        ],
        "answer": "Structured Query Language"
    },
    {
        "question": "Which command is used to retrieve data from a database?",
        "options": ["GET", "SELECT", "OPEN", "FETCH ALL"],
        "answer": "SELECT"
    }
]

# -------------------- DATABASE --------------------
def create_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            score INTEGER,
            total INTEGER,
            percentage REAL,
            date TEXT
        )
    """)
    connection.commit()
    connection.close()


def save_result(name, score, total):
    percentage = (score / total) * 100
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO results (student_name, score, total, percentage, date) VALUES (?, ?, ?, ?, ?)",
        (name, score, total, percentage, time.strftime("%Y-%m-%d %H:%M:%S"))
    )
    connection.commit()
    connection.close()


def get_results():
    connection = sqlite3.connect(DB_NAME)
    data = pd.read_sql_query("SELECT * FROM results ORDER BY id DESC", connection)
    connection.close()
    return data


create_database()

# -------------------- SESSION SETTINGS --------------------
if "exam_started" not in st.session_state:
    st.session_state.exam_started = False
if "exam_submitted" not in st.session_state:
    st.session_state.exam_submitted = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "last_score" not in st.session_state:
    st.session_state.last_score = None

# -------------------- SIDEBAR --------------------
st.sidebar.title("📝 Smart CBT")
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Take Examination", "Results", "Performance Analysis"]
)

st.title("📝 Smart CBT Examination System")
st.caption("A simple computer-based examination project built with Python and Streamlit.")

# -------------------- HOME --------------------
if page == "Home":
    st.subheader("Welcome to the Examination Portal")
    st.write(
        "This system allows students to take timed MCQ examinations, "
        "receive automatic results, and view their performance."
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", len(QUESTIONS))
    col2.metric("Exam Duration", f"{EXAM_DURATION} minutes")
    col3.metric("Question Type", "MCQ")
    st.info("Open 'Take Examination' from the sidebar to begin.")

# -------------------- EXAMINATION --------------------
elif page == "Take Examination":
    st.subheader("Student Examination")

    if not st.session_state.exam_started and not st.session_state.exam_submitted:
        name = st.text_input("Enter your name")
        st.write(f"**Total questions:** {len(QUESTIONS)}")
        st.write(f"**Time limit:** {EXAM_DURATION} minutes")
        st.write("Each correct answer carries 1 mark. There is no negative marking.")

        if st.button("Start Examination", type="primary"):
            if name.strip():
                st.session_state.student_name = name.strip()
                st.session_state.start_time = time.time()
                st.session_state.exam_started = True
                st.rerun()
            else:
                st.warning("Please enter your name first.")

    if st.session_state.exam_started and not st.session_state.exam_submitted:
        # Refresh the page every second so the countdown stays updated.
        st_autorefresh(interval=1000, key="exam_timer_refresh")
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, EXAM_DURATION * 60 - int(elapsed))
        minutes = remaining // 60
        seconds = remaining % 60

        st.warning(f"Time remaining: {minutes:02d}:{seconds:02d}")
        st.progress(remaining / (EXAM_DURATION * 60))

        with st.form("exam_form"):
            answers = {}
            for number, question in enumerate(QUESTIONS, start=1):
                st.markdown(f"**Q{number}. {question['question']}**")
                answers[number] = st.radio(
                    "Choose your answer",
                    question["options"],
                    index=None,
                    key=f"answer_{number}",
                    label_visibility="collapsed"
                )
                st.divider()

            submitted = st.form_submit_button("Submit Examination")

        if submitted or remaining <= 0:
            score = 0
            for number, question in enumerate(QUESTIONS, start=1):
                if answers.get(number) == question["answer"]:
                    score += 1

            save_result(st.session_state.student_name, score, len(QUESTIONS))
            st.session_state.last_score = score
            st.session_state.exam_started = False
            st.session_state.exam_submitted = True
            st.rerun()

    if st.session_state.exam_submitted:
        score = st.session_state.last_score
        percentage = (score / len(QUESTIONS)) * 100
        st.success("Your examination has been submitted!")
        st.metric("Your Score", f"{score} / {len(QUESTIONS)}")
        st.metric("Percentage", f"{percentage:.1f}%")
        if percentage >= 40:
            st.success("Result: Pass")
        else:
            st.error("Result: Needs Improvement")
        if st.button("Start a New Examination"):
            st.session_state.exam_submitted = False
            st.session_state.last_score = None
            st.rerun()

# -------------------- RESULTS --------------------
elif page == "Results":
    st.subheader("Examination Results")
    data = get_results()
    if data.empty:
        st.info("No examination results are available yet.")
    else:
        st.dataframe(data[["student_name", "score", "total", "percentage", "date"]],
                     use_container_width=True, hide_index=True)
        csv_data = data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Results as CSV",
            data=csv_data,
            file_name="cbt_results.csv",
            mime="text/csv"
        )

# -------------------- PERFORMANCE ANALYSIS --------------------
elif page == "Performance Analysis":
    st.subheader("Student Performance Analysis")
    data = get_results()

    if data.empty:
        st.info("Take an examination first to see performance analysis.")
    else:
        names = sorted(data["student_name"].unique().tolist())
        selected_name = st.selectbox("Select student", names)
        student_data = data[data["student_name"] == selected_name].sort_values("id")

        average = student_data["percentage"].mean()
        highest = student_data["percentage"].max()
        attempts = len(student_data)

        col1, col2, col3 = st.columns(3)
        col1.metric("Examinations Attempted", attempts)
        col2.metric("Average Percentage", f"{average:.1f}%")
        col3.metric("Highest Percentage", f"{highest:.1f}%")

        chart = px.line(
            student_data,
            x="date",
            y="percentage",
            markers=True,
            title=f"Performance Progress – {selected_name}",
            labels={"date": "Examination Date", "percentage": "Percentage"}
        )
        chart.update_yaxes(range=[0, 100])
        st.plotly_chart(chart, use_container_width=True)

        # Simple rule-based estimate, not a trained machine-learning model.
        if attempts == 1:
            prediction = average
            st.info("Prediction is based on one attempt. Take more exams for a more useful estimate.")
        else:
            prediction = student_data.tail(3)["percentage"].mean()

        st.markdown("### Future Performance Prediction")
        st.metric("Estimated Next Exam Percentage", f"{prediction:.1f}%")
        if prediction >= 75:
            st.success("Prediction: Excellent performance range")
        elif prediction >= 50:
            st.info("Prediction: Good performance range")
        elif prediction >= 40:
            st.warning("Prediction: Average performance range")
        else:
            st.error("Prediction: More practice is recommended")

        st.caption(
            "This is a basic estimate using the average of the latest three attempts. "
            "It is for learning and demonstration, not a guaranteed prediction."
        )

st.sidebar.divider()
st.sidebar.caption("Student Project | Python + Streamlit + SQLite")
