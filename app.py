import sqlite3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="CareerPilot AI API",
    description="Backend API for AI Career and Student Preparation Platform",
    version="1.0.0"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    connection = sqlite3.connect("content_studio.db")
    connection.row_factory = sqlite3.Row
    return connection


# =========================================================
# DATABASE TABLES
# =========================================================

def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # Student Profile
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            degree TEXT NOT NULL,
            branch TEXT NOT NULL,
            graduation_year INTEGER NOT NULL,
            skills TEXT NOT NULL,
            target_role TEXT NOT NULL,
            target_company TEXT,
            daily_study_hours INTEGER NOT NULL
        )
    """)

    # DSA Attempts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dsa_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            status TEXT NOT NULL,
            time_taken_minutes INTEGER NOT NULL,
            attempt_number INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    connection.commit()
    connection.close()


create_tables()


# =========================================================
# MODELS
# =========================================================

class Student(BaseModel):

    name: str = Field(min_length=2)
    degree: str = Field(min_length=2)
    branch: str = Field(min_length=2)
    graduation_year: int = Field(ge=2000, le=2100)
    skills: str = Field(min_length=1)
    target_role: str = Field(min_length=2)
    target_company: str | None = None
    daily_study_hours: int = Field(ge=1, le=24)


class DSAAttempt(BaseModel):

    student_id: int = Field(ge=1)
    question: str = Field(min_length=3)
    topic: str = Field(min_length=2)
    difficulty: str = Field(min_length=3)
    status: str = Field(min_length=3)
    time_taken_minutes: int = Field(ge=1)
    attempt_number: int = Field(default=1, ge=1)


# =========================================================
# BASIC ROUTES
# =========================================================

@app.get("/")
def home():

    return {
        "message": "CareerPilot AI API is running!"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# =========================================================
# CREATE STUDENT
# =========================================================

@app.post("/students")
def create_student(student: Student):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO students (
            name,
            degree,
            branch,
            graduation_year,
            skills,
            target_role,
            target_company,
            daily_study_hours
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student.name,
        student.degree,
        student.branch,
        student.graduation_year,
        student.skills,
        student.target_role,
        student.target_company,
        student.daily_study_hours
    ))

    student_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "message": "Student profile created successfully",
        "student_id": student_id
    }


# =========================================================
# GET ALL STUDENTS
# =========================================================

@app.get("/students")
def get_all_students(

    search: str | None = Query(default=None),

    target_role: str | None = Query(default=None),

    target_company: str | None = Query(default=None),

    page: int = Query(default=1, ge=1),

    limit: int = Query(default=10, ge=1, le=100)
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT *
        FROM students
        WHERE 1=1
    """

    parameters = []

    # Search
    if search:

        query += """
            AND (
                name LIKE ?
                OR branch LIKE ?
                OR skills LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value
        ])

    # Target Role Filter
    if target_role:

        query += """
            AND target_role LIKE ?
        """

        parameters.append(
            f"%{target_role}%"
        )

    # Target Company Filter
    if target_company:

        query += """
            AND target_company LIKE ?
        """

        parameters.append(
            f"%{target_company}%"
        )

    # Pagination
    offset = (page - 1) * limit

    query += """
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """

    parameters.extend([
        limit,
        offset
    ])

    cursor.execute(
        query,
        parameters
    )

    rows = cursor.fetchall()

    students = [
        dict(row)
        for row in rows
    ]

    connection.close()

    return {
        "page": page,
        "limit": limit,
        "count": len(students),
        "students": students
    }


# =========================================================
# GET STUDENT BY ID
# =========================================================

@app.get("/students/{student_id}")
def get_student(student_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    return dict(row)


# =========================================================
# UPDATE STUDENT
# =========================================================

@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    student: Student
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    existing_student = cursor.fetchone()

    if existing_student is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    cursor.execute("""
        UPDATE students
        SET
            name = ?,
            degree = ?,
            branch = ?,
            graduation_year = ?,
            skills = ?,
            target_role = ?,
            target_company = ?,
            daily_study_hours = ?
        WHERE id = ?
    """, (
        student.name,
        student.degree,
        student.branch,
        student.graduation_year,
        student.skills,
        student.target_role,
        student.target_company,
        student.daily_study_hours,
        student_id
    ))

    connection.commit()
    connection.close()

    return {
        "message": "Student profile updated successfully",
        "student_id": student_id
    }


# =========================================================
# DELETE STUDENT
# =========================================================

@app.delete("/students/{student_id}")
def delete_student(student_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    existing_student = cursor.fetchone()

    if existing_student is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    cursor.execute(
        """
        DELETE FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Student profile deleted successfully",
        "student_id": student_id
    }


# =========================================================
# CAREER ROADMAP
# =========================================================

@app.get("/students/{student_id}/roadmap")
def get_career_roadmap(student_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    student = dict(row)

    target_role = student["target_role"].lower()

    current_skills = [
        skill.strip().lower()
        for skill in student["skills"].split(",")
        if skill.strip()
    ]

    # =====================================================
    # SOFTWARE DEVELOPMENT ROADMAP
    # =====================================================

    if (
        "software" in target_role
        or "developer" in target_role
        or "sde" in target_role
        or "software engineer" in target_role
    ):

        roadmap = [

            {
                "phase": 1,
                "title": "Programming Fundamentals",
                "skills": [
                    "Python",
                    "Programming Logic",
                    "Functions",
                    "Exception Handling",
                    "Object Oriented Programming"
                ]
            },

            {
                "phase": 2,
                "title": "Data Structures & Algorithms",
                "skills": [
                    "Arrays",
                    "Strings",
                    "Linked Lists",
                    "Stacks",
                    "Queues",
                    "Trees",
                    "Graphs",
                    "Sorting",
                    "Searching",
                    "Dynamic Programming"
                ]
            },

            {
                "phase": 3,
                "title": "Computer Science Fundamentals",
                "skills": [
                    "DBMS",
                    "SQL",
                    "Operating Systems",
                    "Computer Networks",
                    "OOP",
                    "Git"
                ]
            },

            {
                "phase": 4,
                "title": "Backend & Software Engineering",
                "skills": [
                    "FastAPI",
                    "REST APIs",
                    "SQL Databases",
                    "Authentication",
                    "Testing",
                    "Docker"
                ]
            },

            {
                "phase": 5,
                "title": "Cloud & System Design",
                "skills": [
                    "AWS",
                    "System Design",
                    "Scalability",
                    "Caching",
                    "Distributed Systems"
                ]
            },

            {
                "phase": 6,
                "title": "Interview Preparation",
                "skills": [
                    "DSA Problems",
                    "Coding Interviews",
                    "System Design Interviews",
                    "Behavioral Interviews",
                    "Resume Preparation"
                ]
            }

        ]

    # =====================================================
    # DATA SCIENCE ROADMAP
    # =====================================================

    elif (
        "data scientist" in target_role
        or "data science" in target_role
    ):

        roadmap = [

            {
                "phase": 1,
                "title": "Python & Mathematics",
                "skills": [
                    "Python",
                    "Statistics",
                    "Probability",
                    "Linear Algebra"
                ]
            },

            {
                "phase": 2,
                "title": "Data Analysis",
                "skills": [
                    "NumPy",
                    "Pandas",
                    "Data Cleaning",
                    "Data Visualization"
                ]
            },

            {
                "phase": 3,
                "title": "Machine Learning",
                "skills": [
                    "Regression",
                    "Classification",
                    "Clustering",
                    "Model Evaluation"
                ]
            },

            {
                "phase": 4,
                "title": "Projects",
                "skills": [
                    "ML Projects",
                    "Feature Engineering",
                    "Model Deployment"
                ]
            },

            {
                "phase": 5,
                "title": "Interview Preparation",
                "skills": [
                    "ML Questions",
                    "Python Questions",
                    "SQL",
                    "Statistics",
                    "Resume Preparation"
                ]
            }

        ]

    # =====================================================
    # GENERAL ROADMAP
    # =====================================================

    else:

        roadmap = [

            {
                "phase": 1,
                "title": "Core Skills",
                "skills": [
                    "Programming Fundamentals",
                    "Problem Solving",
                    "Communication"
                ]
            },

            {
                "phase": 2,
                "title": "Technical Skills",
                "skills": [
                    "Role Specific Skills",
                    "Databases",
                    "Git"
                ]
            },

            {
                "phase": 3,
                "title": "Projects",
                "skills": [
                    "Real World Project",
                    "GitHub Portfolio",
                    "Testing"
                ]
            },

            {
                "phase": 4,
                "title": "Interview Preparation",
                "skills": [
                    "Technical Interview",
                    "Resume",
                    "Behavioral Interview"
                ]
            }

        ]

    # =====================================================
    # PROGRESS CALCULATION
    # =====================================================

    total_skills = 0
    completed_skills = 0

    for phase in roadmap:

        for skill in phase["skills"]:

            total_skills += 1

            skill_lower = skill.lower()

            if any(
                skill_lower in current_skill
                or current_skill in skill_lower
                for current_skill in current_skills
            ):

                completed_skills += 1

    if total_skills > 0:

        progress = round(
            (completed_skills / total_skills) * 100
        )

    else:

        progress = 0

    return {

        "student": student["name"],

        "target_role": student["target_role"],

        "target_company": student["target_company"],

        "daily_study_hours": student["daily_study_hours"],

        "roadmap_progress": f"{progress}%",

        "completed_skills": completed_skills,

        "total_skills": total_skills,

        "roadmap": roadmap
    }


# =========================================================
# DSA PRACTICE TRACKER
# =========================================================

@app.post("/dsa/attempts")
def create_dsa_attempt(attempt: DSAAttempt):

    connection = get_connection()
    cursor = connection.cursor()

    # Check student exists
    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE id = ?
        """,
        (attempt.student_id,)
    )

    student = cursor.fetchone()

    if student is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    # Validate difficulty
    allowed_difficulties = {
        "easy",
        "medium",
        "hard"
    }

    difficulty = attempt.difficulty.lower()

    if difficulty not in allowed_difficulties:

        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Difficulty must be Easy, Medium or Hard"
        )

    # Validate status
    allowed_status = {
        "solved",
        "failed"
    }

    status = attempt.status.lower()

    if status not in allowed_status:

        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Status must be Solved or Failed"
        )

    cursor.execute("""
        INSERT INTO dsa_attempts (
            student_id,
            question,
            topic,
            difficulty,
            status,
            time_taken_minutes,
            attempt_number
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (

        attempt.student_id,

        attempt.question,

        attempt.topic,

        difficulty.title(),

        status.title(),

        attempt.time_taken_minutes,

        attempt.attempt_number

    ))

    attempt_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {

        "message": "DSA attempt recorded successfully",

        "attempt_id": attempt_id

    }


# =========================================================
# GET DSA ATTEMPTS
# =========================================================

@app.get("/students/{student_id}/dsa")
def get_dsa_attempts(

    student_id: int,

    topic: str | None = Query(default=None),

    difficulty: str | None = Query(default=None),

    status: str | None = Query(default=None)

):

    connection = get_connection()
    cursor = connection.cursor()

    # Check student
    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    query = """
        SELECT *
        FROM dsa_attempts
        WHERE student_id = ?
    """

    parameters = [
        student_id
    ]

    # Topic filter
    if topic:

        query += """
            AND topic LIKE ?
        """

        parameters.append(
            f"%{topic}%"
        )

    # Difficulty filter
    if difficulty:

        query += """
            AND difficulty = ?
        """

        parameters.append(
            difficulty.title()
        )

    # Status filter
    if status:

        query += """
            AND status = ?
        """

        parameters.append(
            status.title()
        )

    query += """
        ORDER BY id DESC
    """

    cursor.execute(
        query,
        parameters
    )

    rows = cursor.fetchall()

    attempts = [
        dict(row)
        for row in rows
    ]

    connection.close()

    return {

        "student_id": student_id,

        "count": len(attempts),

        "attempts": attempts

    }


# =========================================================
# DSA PERFORMANCE SUMMARY
# =========================================================

@app.get("/students/{student_id}/dsa/summary")
def get_dsa_summary(student_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    # Check student
    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    # Total attempts
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM dsa_attempts
        WHERE student_id = ?
        """,
        (student_id,)
    )

    total_attempts = cursor.fetchone()["total"]

    # Solved
    cursor.execute(
        """
        SELECT COUNT(*) AS solved
        FROM dsa_attempts
        WHERE student_id = ?
        AND status = 'Solved'
        """,
        (student_id,)
    )

    solved = cursor.fetchone()["solved"]

    # Failed
    cursor.execute(
        """
        SELECT COUNT(*) AS failed
        FROM dsa_attempts
        WHERE student_id = ?
        AND status = 'Failed'
        """,
        (student_id,)
    )

    failed = cursor.fetchone()["failed"]

    # Topic performance
    cursor.execute(
        """
        SELECT
            topic,
            COUNT(*) AS attempts,
            SUM(
                CASE
                    WHEN status = 'Solved'
                    THEN 1
                    ELSE 0
                END
            ) AS solved
        FROM dsa_attempts
        WHERE student_id = ?
        GROUP BY topic
        ORDER BY solved ASC
        """,
        (student_id,)
    )

    topic_rows = cursor.fetchall()

    topic_performance = []

    for row in topic_rows:

        attempts = row["attempts"]

        topic_solved = row["solved"]

        percentage = round(
            (topic_solved / attempts) * 100
        )

        topic_performance.append({

            "topic": row["topic"],

            "attempts": attempts,

            "solved": topic_solved,

            "success_rate": f"{percentage}%"

        })

    # Difficulty performance
    cursor.execute(
        """
        SELECT
            difficulty,
            COUNT(*) AS attempts,
            SUM(
                CASE
                    WHEN status = 'Solved'
                    THEN 1
                    ELSE 0
                END
            ) AS solved
        FROM dsa_attempts
        WHERE student_id = ?
        GROUP BY difficulty
        """,
        (student_id,)
    )

    difficulty_rows = cursor.fetchall()

    difficulty_performance = []

    for row in difficulty_rows:

        attempts = row["attempts"]

        difficulty_solved = row["solved"]

        percentage = round(
            (difficulty_solved / attempts) * 100
        )

        difficulty_performance.append({

            "difficulty": row["difficulty"],

            "attempts": attempts,

            "solved": difficulty_solved,

            "success_rate": f"{percentage}%"

        })

    # Overall success rate
    if total_attempts > 0:

        success_rate = round(
            (solved / total_attempts) * 100
        )

    else:

        success_rate = 0

    connection.close()

    return {

        "student_id": student_id,

        "total_attempts": total_attempts,

        "solved": solved,

        "failed": failed,

        "overall_success_rate": f"{success_rate}%",

        "topic_performance": topic_performance,

        "difficulty_performance": difficulty_performance

    }
# =========================================================
# DSA WEAKNESS ANALYSIS
# =========================================================

@app.get("/students/{student_id}/dsa/weakness")
def get_dsa_weakness(student_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    # Check student
    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    # Get topic performance
    cursor.execute(
        """
        SELECT
            topic,
            COUNT(*) AS attempts,
            SUM(
                CASE
                    WHEN status = 'Solved'
                    THEN 1
                    ELSE 0
                END
            ) AS solved
        FROM dsa_attempts
        WHERE student_id = ?
        GROUP BY topic
        """,
        (student_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    if not rows:
        return {
            "student_id": student_id,
            "message": "No DSA practice data available yet.",
            "weak_topics": [],
            "strong_topics": [],
            "recommendation": "Start solving DSA questions."
        }

    weak_topics = []
    strong_topics = []

    for row in rows:

        topic = row["topic"]
        attempts = row["attempts"]
        solved = row["solved"]

        success_rate = round(
            (solved / attempts) * 100
        )

        topic_data = {
            "topic": topic,
            "attempts": attempts,
            "solved": solved,
            "success_rate": f"{success_rate}%"
        }

        # Weak = success rate below 60%
        if success_rate < 60:
            weak_topics.append(topic_data)

        # Strong = success rate 80% or above
        elif success_rate >= 80:
            strong_topics.append(topic_data)

    # Sort weak topics by lowest success rate
    weak_topics.sort(
        key=lambda x: int(
            x["success_rate"].replace("%", "")
        )
    )

    # Sort strong topics by highest success rate
    strong_topics.sort(
        key=lambda x: int(
            x["success_rate"].replace("%", "")
        ),
        reverse=True
    )

    if weak_topics:

        priority_topic = weak_topics[0]["topic"]

        recommendation = (
            f"Focus on {priority_topic} first. "
            f"Practice more questions and review the concepts "
            f"before moving to harder problems."
        )

    elif strong_topics:

        priority_topic = strong_topics[-1]["topic"]

        recommendation = (
            "Your current DSA performance is good. "
            f"Next, increase difficulty and practice {priority_topic} "
            "with Medium and Hard questions."
        )

    else:

        recommendation = (
            "Keep practicing across different DSA topics "
            "to generate enough performance data."
        )

    return {
        "student_id": student_id,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "recommendation": recommendation
    }
# =========================================================
# CAREER READINESS SCORE
# =========================================================

@app.get("/students/{student_id}/readiness")
def get_readiness_score(student_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    # -----------------------------------------------------
    # Get student profile
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    student = dict(student)

    # -----------------------------------------------------
    # DSA SCORE
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total,
            SUM(
                CASE
                    WHEN status = 'Solved'
                    THEN 1
                    ELSE 0
                END
            ) AS solved
        FROM dsa_attempts
        WHERE student_id = ?
        """,
        (student_id,)
    )

    dsa_data = cursor.fetchone()

    total_dsa = dsa_data["total"]
    solved_dsa = dsa_data["solved"] or 0

    if total_dsa > 0:

        dsa_score = round(
            (solved_dsa / total_dsa) * 100
        )

    else:

        dsa_score = 0

    # -----------------------------------------------------
    # PROJECT / BACKEND SCORE
    # -----------------------------------------------------

    project_score = 0

    skills = [
        skill.strip().lower()
        for skill in student["skills"].split(",")
        if skill.strip()
    ]

    project_skills = {
        "fastapi",
        "rest api",
        "sql",
        "docker",
        "aws",
        "git",
        "backend"
    }

    matching_project_skills = 0

    for skill in project_skills:

        if any(
            skill in current_skill
            or current_skill in skill
            for current_skill in skills
        ):

            matching_project_skills += 1

    project_score = round(
        (
            matching_project_skills
            / len(project_skills)
        ) * 100
    )

    # -----------------------------------------------------
    # CORE CS SCORE
    # -----------------------------------------------------

    core_skills = {
        "dbms",
        "sql",
        "operating systems",
        "computer networks",
        "oop"
    }

    matching_core_skills = 0

    for skill in core_skills:

        if any(
            skill in current_skill
            or current_skill in skill
            for current_skill in skills
        ):

            matching_core_skills += 1

    core_cs_score = round(
        (
            matching_core_skills
            / len(core_skills)
        ) * 100
    )

    # -----------------------------------------------------
    # CAREER PREPARATION SCORE
    # -----------------------------------------------------

    preparation_score = 0

    preparation_skills = {
        "python",
        "git",
        "communication",
        "resume",
        "interview"
    }

    matching_preparation_skills = 0

    for skill in preparation_skills:

        if any(
            skill in current_skill
            or current_skill in skill
            for current_skill in skills
        ):

            matching_preparation_skills += 1

    preparation_score = round(
        (
            matching_preparation_skills
            / len(preparation_skills)
        ) * 100
    )

    # -----------------------------------------------------
    # FINAL WEIGHTED SCORE
    # -----------------------------------------------------

    readiness_score = round(
        (
            dsa_score * 0.40
            +
            project_score * 0.25
            +
            core_cs_score * 0.20
            +
            preparation_score * 0.15
        )
    )

    # -----------------------------------------------------
    # READINESS LEVEL
    # -----------------------------------------------------

    if readiness_score >= 80:

        readiness_level = "Job Ready"

    elif readiness_score >= 60:

        readiness_level = "Almost Ready"

    elif readiness_score >= 40:

        readiness_level = "Needs Improvement"

    else:

        readiness_level = "Beginner"

    # -----------------------------------------------------
    # RECOMMENDATION
    # -----------------------------------------------------

    scores = {
        "DSA": dsa_score,
        "Projects & Backend": project_score,
        "Core CS": core_cs_score,
        "Career Preparation": preparation_score
    }

    weakest_area = min(
        scores,
        key=scores.get
    )

    recommendation = (
        f"Your weakest area is {weakest_area}. "
        f"Focus on improving this area before moving "
        f"to advanced interview preparation."
    )

    connection.close()

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "student_id": student_id,

        "student": student["name"],

        "target_role": student["target_role"],

        "target_company": student["target_company"],

        "career_readiness_score": readiness_score,

        "readiness_level": readiness_level,

        "score_breakdown": scores,

        "recommendation": recommendation

    }
# =========================================================
# STUDY PLANNER
# =========================================================

@app.get("/students/{student_id}/study-plan")
def get_study_plan(student_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    student = dict(student)

    daily_hours = student["daily_study_hours"]
    target_role = student["target_role"]

    # -----------------------------------------------------
    # DAILY TIME ALLOCATION
    # -----------------------------------------------------

    dsa_hours = round(daily_hours * 0.40, 1)
    core_cs_hours = round(daily_hours * 0.20, 1)
    development_hours = round(daily_hours * 0.25, 1)
    revision_hours = round(daily_hours * 0.15, 1)

    # Make sure minimum practical values exist
    if dsa_hours == 0:
        dsa_hours = 0.5

    if development_hours == 0:
        development_hours = 0.5

    # -----------------------------------------------------
    # WEEKLY PLAN
    # -----------------------------------------------------

    weekly_plan = [

        {
            "day": "Monday",
            "focus": "DSA",
            "hours": dsa_hours,
            "tasks": [
                "Learn one DSA concept",
                "Solve 2 Easy questions",
                "Review mistakes"
            ]
        },

        {
            "day": "Tuesday",
            "focus": "Core CS",
            "hours": core_cs_hours,
            "tasks": [
                "Study DBMS / Operating Systems",
                "Make short notes",
                "Practice interview questions"
            ]
        },

        {
            "day": "Wednesday",
            "focus": "DSA",
            "hours": dsa_hours,
            "tasks": [
                "Practice Arrays / Strings / Linked Lists",
                "Solve 2-3 questions",
                "Analyze failed attempts"
            ]
        },

        {
            "day": "Thursday",
            "focus": "Development",
            "hours": development_hours,
            "tasks": [
                "Build project feature",
                "Practice FastAPI / SQL",
                "Write clean code"
            ]
        },

        {
            "day": "Friday",
            "focus": "DSA",
            "hours": dsa_hours,
            "tasks": [
                "Solve Medium-level questions",
                "Practice timed coding",
                "Review weak topics"
            ]
        },

        {
            "day": "Saturday",
            "focus": "Project + Interview",
            "hours": development_hours + revision_hours,
            "tasks": [
                "Work on CareerPilot project",
                "Practice coding interview",
                "Improve GitHub project"
            ]
        },

        {
            "day": "Sunday",
            "focus": "Revision + Mock Test",
            "hours": revision_hours + dsa_hours,
            "tasks": [
                "Revise week's concepts",
                "Take a DSA mock test",
                "Review performance",
                "Plan next week"
            ]
        }

    ]

    # -----------------------------------------------------
    # WEEKLY HOURS
    # -----------------------------------------------------

    weekly_hours = round(
        daily_hours * 7,
        1
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    connection.close()

    return {

        "student": student["name"],

        "target_role": target_role,

        "daily_study_hours": daily_hours,

        "weekly_study_hours": weekly_hours,

        "plan_type": "Personalized Weekly Study Plan",

        "weekly_plan": weekly_plan,

        "message": (
            "Follow this plan consistently and update your "
            "DSA attempts regularly so CareerPilot can "
            "personalize your preparation further."
        )

    }
# =========================================================
# JOB APPLICATION TRACKER
# =========================================================

class JobApplication(BaseModel):

    student_id: int = Field(ge=1)
    company: str = Field(min_length=2)
    role: str = Field(min_length=2)
    location: str | None = None
    application_date: str = Field(min_length=8)
    status: str = Field(min_length=2)
    interview_stage: str | None = None
    notes: str | None = None


# =========================================================
# JOB APPLICATION TABLE
# =========================================================

def create_job_application_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            application_date TEXT NOT NULL,
            status TEXT NOT NULL,
            interview_stage TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    connection.commit()
    connection.close()


create_job_application_table()


# =========================================================
# ADD JOB APPLICATION
# =========================================================

@app.post("/jobs/applications")
def create_job_application(application: JobApplication):

    connection = get_connection()
    cursor = connection.cursor()

    # Check student
    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE id = ?
        """,
        (application.student_id,)
    )

    student = cursor.fetchone()

    if student is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    # Allowed statuses
    allowed_statuses = {
        "applied",
        "oa",
        "interview",
        "offer",
        "rejected",
        "withdrawn"
    }

    status = application.status.lower()

    if status not in allowed_statuses:

        connection.close()

        raise HTTPException(
            status_code=400,
            detail=(
                "Status must be one of: "
                "Applied, OA, Interview, Offer, "
                "Rejected or Withdrawn"
            )
        )

    cursor.execute("""
        INSERT INTO job_applications (
            student_id,
            company,
            role,
            location,
            application_date,
            status,
            interview_stage,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        application.student_id,
        application.company,
        application.role,
        application.location,
        application.application_date,
        status.title(),
        application.interview_stage,
        application.notes

    ))

    application_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {

        "message": "Job application added successfully",

        "application_id": application_id

    }


# =========================================================
# GET JOB APPLICATIONS
# =========================================================

@app.get("/students/{student_id}/jobs")
def get_job_applications(

    student_id: int,

    status: str | None = Query(default=None),

    company: str | None = Query(default=None)

):

    connection = get_connection()
    cursor = connection.cursor()

    # Check student
    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    query = """
        SELECT *
        FROM job_applications
        WHERE student_id = ?
    """

    parameters = [
        student_id
    ]

    # Status filter
    if status:

        query += """
            AND status = ?
        """

        parameters.append(
            status.title()
        )

    # Company filter
    if company:

        query += """
            AND company LIKE ?
        """

        parameters.append(
            f"%{company}%"
        )

    query += """
        ORDER BY id DESC
    """

    cursor.execute(
        query,
        parameters
    )

    rows = cursor.fetchall()

    applications = [
        dict(row)
        for row in rows
    ]

    connection.close()

    return {

        "student_id": student_id,

        "count": len(applications),

        "applications": applications

    }


# =========================================================
# JOB APPLICATION SUMMARY
# =========================================================

@app.get("/students/{student_id}/jobs/summary")
def get_job_summary(student_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    # Check student
    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    # Total applications
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM job_applications
        WHERE student_id = ?
        """,
        (student_id,)
    )

    total = cursor.fetchone()["total"]

    # Applications by status
    cursor.execute(
        """
        SELECT
            status,
            COUNT(*) AS count
        FROM job_applications
        WHERE student_id = ?
        GROUP BY status
        ORDER BY count DESC
        """,
        (student_id,)
    )

    status_rows = cursor.fetchall()

    status_summary = {}

    for row in status_rows:

        status_summary[row["status"]] = row["count"]

    # Interview count
    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM job_applications
        WHERE student_id = ?
        AND status = 'Interview'
        """,
        (student_id,)
    )

    interviews = cursor.fetchone()["count"]

    # Offer count
    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM job_applications
        WHERE student_id = ?
        AND status = 'Offer'
        """,
        (student_id,)
    )

    offers = cursor.fetchone()["count"]

    # Rejection count
    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM job_applications
        WHERE student_id = ?
        AND status = 'Rejected'
        """,
        (student_id,)
    )

    rejected = cursor.fetchone()["count"]

    # Interview conversion rate
    if total > 0:

        interview_rate = round(
            (interviews / total) * 100
        )

    else:

        interview_rate = 0

    # Offer conversion rate
    if total > 0:

        offer_rate = round(
            (offers / total) * 100
        )

    else:

        offer_rate = 0

    connection.close()

    return {

        "student_id": student_id,

        "total_applications": total,

        "status_summary": status_summary,

        "interviews": interviews,

        "offers": offers,

        "rejected": rejected,

        "interview_conversion_rate": f"{interview_rate}%",

        "offer_conversion_rate": f"{offer_rate}%"

    }
# =========================================================
# USER AUTHENTICATION
# =========================================================

from passlib.context import CryptContext


# =========================================================
# PASSWORD SECURITY
# =========================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =========================================================
# USER MODEL
# =========================================================

class UserCreate(BaseModel):

    name: str = Field(min_length=2)

    email: str = Field(min_length=5)

    password: str = Field(min_length=6)


class UserLogin(BaseModel):

    email: str = Field(min_length=5)

    password: str = Field(min_length=6)


# =========================================================
# USERS TABLE
# =========================================================

def create_users_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


create_users_table()


# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password: str):

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str
):

    return pwd_context.verify(
        plain_password,
        password_hash
    )


# =========================================================
# REGISTER USER
# =========================================================

@app.post("/auth/register")
def register_user(user: UserCreate):

    connection = get_connection()
    cursor = connection.cursor()

    # Check existing email
    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE email = ?
        """,
        (user.email.lower(),)
    )

    existing_user = cursor.fetchone()

    if existing_user:

        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    password_hash = hash_password(
        user.password
    )

    # Create user
    cursor.execute(
        """
        INSERT INTO users (
            name,
            email,
            password_hash
        )
        VALUES (?, ?, ?)
        """,
        (
            user.name,
            user.email.lower(),
            password_hash
        )
    )

    user_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {

        "message": "User registered successfully",

        "user_id": user_id,

        "name": user.name,

        "email": user.email.lower()

    }


# =========================================================
# LOGIN USER
# =========================================================

@app.post("/auth/login")
def login_user(user: UserLogin):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (user.email.lower(),)
    )

    existing_user = cursor.fetchone()

    connection.close()

    if existing_user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_correct = verify_password(
        user.password,
        existing_user["password_hash"]
    )

    if not password_correct:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {

        "message": "Login successful",

        "user_id": existing_user["id"],

        "name": existing_user["name"],

        "email": existing_user["email"]

    }