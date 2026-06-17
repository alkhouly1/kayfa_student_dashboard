import os
import textwrap
import base64
from io import BytesIO

import certifi
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from pymongo import MongoClient

try:
    from PIL import Image
except Exception:
    Image = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Kayfa Student Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SETTINGS
# ============================================================

DEBUG_MONGO = True


# ============================================================
# CSS — DARK BLUE EXECUTIVE THEME
# ============================================================

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #041226 0%, #061A35 55%, #041226 100%);
            color: #EAF3FF;
        }

        section[data-testid="stSidebar"] {
            background: #06162E;
            border-right: 1px solid rgba(255,255,255,0.12);
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 3rem;
            max-width: 1650px;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
            font-weight: 900 !important;
            letter-spacing: -0.4px;
        }

        p, span, label, div {
            color: #EAF3FF;
        }

        .logo-card {
            background: #F4F9FF;
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 18px;
            padding: 14px 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 22px rgba(0,0,0,0.22);
            margin-bottom: 10px;
        }

        .hero {
            background: linear-gradient(135deg, #082A5B 0%, #114C96 100%);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 26px;
            padding: 28px 32px;
            margin-bottom: 24px;
            box-shadow: 0 16px 45px rgba(0,0,0,0.35);
        }

        .hero-title {
            font-size: 42px;
            line-height: 1.1;
            font-weight: 950;
            color: #FFFFFF;
            margin-bottom: 8px;
        }

        .hero-subtitle {
            color: #BFD9FF;
            font-size: 18px;
            line-height: 1.5;
        }

        .kpi-card {
            background: rgba(8, 34, 72, 0.96);
            border: 1px solid rgba(255,255,255,0.13);
            border-radius: 22px;
            padding: 22px 22px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.28);
            min-height: 145px;
        }

        .kpi-title {
            color: #BFD9FF;
            font-size: 15px;
            font-weight: 800;
            margin-bottom: 10px;
        }

        .kpi-value {
            color: #FFFFFF;
            font-size: 36px;
            font-weight: 950;
            margin-bottom: 8px;
        }

        .kpi-note {
            color: #96BCEB;
            font-size: 14px;
        }

        .insight-box {
            background: rgba(78, 161, 255, 0.16);
            border-left: 6px solid #4EA1FF;
            border-radius: 16px;
            padding: 18px 20px;
            margin-top: 16px;
            margin-bottom: 10px;
            font-size: 17px;
            line-height: 1.6;
        }

        .recommend-box {
            background: rgba(54, 211, 153, 0.14);
            border-left: 6px solid #36D399;
            border-radius: 16px;
            padding: 18px 20px;
            margin-top: 10px;
            margin-bottom: 18px;
            font-size: 17px;
            line-height: 1.6;
        }

        .final-rec {
            background: linear-gradient(135deg, rgba(78, 161, 255, 0.20), rgba(54, 211, 153, 0.14));
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 18px;
            padding: 18px 20px;
            margin-bottom: 14px;
            font-size: 18px;
            line-height: 1.6;
            color: #FFFFFF;
        }

        .action-card {
            background: rgba(8, 34, 72, 0.96);
            border: 1px solid rgba(255,255,255,0.13);
            border-radius: 18px;
            padding: 18px 20px;
            margin-bottom: 14px;
            box-shadow: 0 10px 24px rgba(0,0,0,0.24);
        }

        .action-title {
            color: #FFFFFF;
            font-size: 20px;
            font-weight: 950;
            margin-bottom: 8px;
        }

        .action-text {
            color: #C9DFFF;
            font-size: 16px;
            line-height: 1.55;
        }

        .small-muted {
            color: #91B7EC;
            font-size: 14px;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: rgba(8, 34, 72, 0.92);
            border-radius: 14px;
            color: #EAF3FF;
            padding: 12px 18px;
            font-size: 17px;
            font-weight: 850;
        }

        .stTabs [aria-selected="true"] {
            background-color: #1E6BD6 !important;
            color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def html(markup):
    st.markdown(textwrap.dedent(markup).strip(), unsafe_allow_html=True)


def recolored_logo_data_uri(path="kayfa_logo.png", dark_blue=(6, 31, 78)):
    if Image is None or not os.path.exists(path):
        return None

    img = Image.open(path).convert("RGBA")
    arr = np.array(img)

    alpha = arr[:, :, 3]
    visible = alpha > 10

    arr[visible, 0] = dark_blue[0]
    arr[visible, 1] = dark_blue[1]
    arr[visible, 2] = dark_blue[2]

    out = Image.fromarray(arr, "RGBA")
    buffer = BytesIO()
    out.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def render_logo(width=150):
    logo_uri = recolored_logo_data_uri("kayfa_logo.png")

    if logo_uri:
        html(
            f"""
            <div class="logo-card">
                <img src="{logo_uri}" width="{width}">
            </div>
            """
        )
    elif os.path.exists("kayfa_logo.png"):
        st.image("kayfa_logo.png", width=width)
    else:
        st.markdown("## Kayfa")


def kpi_card(title, value, note=""):
    html(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """
    )


def insight(text):
    html(
        f"""
        <div class="insight-box">
            <b>Insight:</b> {text}
        </div>
        """
    )


def recommendation(text):
    html(
        f"""
        <div class="recommend-box">
            <b>Recommendation:</b> {text}
        </div>
        """
    )


def fmt_pct(x):
    if pd.isna(x):
        return "N/A"
    return f"{float(x):.2f}%"


def fmt_num(x):
    if pd.isna(x):
        return "N/A"
    return f"{float(x):,.2f}"


def to_numeric(df, columns):
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def style_fig(fig, height=660):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#EAF3FF", size=17),
        title=dict(font=dict(color="#FFFFFF", size=26), x=0.02),
        legend=dict(
            font=dict(color="#EAF3FF", size=15),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=height,
        margin=dict(l=40, r=40, t=90, b=55),
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)",
        color="#EAF3FF",
        title_font=dict(size=18),
        tickfont=dict(size=15),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)",
        color="#EAF3FF",
        title_font=dict(size=18),
        tickfont=dict(size=15),
    )

    return fig


def show_chart(fig, height=None):
    if height is not None:
        fig.update_layout(height=height)
    st.plotly_chart(fig, width="stretch")


def render_action_cards(df):
    if df.empty:
        st.info("No action plan cards available.")
        return

    for _, row in df.iterrows():
        area = row.get("priority_area", "Priority Area")
        finding = row.get("main_finding", "")
        action = row.get("recommended_action", "")
        impact = row.get("expected_impact", "")

        html(
            f"""
            <div class="action-card">
                <div class="action-title">{area}</div>
                <div class="action-text"><b>Main Finding:</b> {finding}</div>
                <div class="action-text"><b>Recommended Action:</b> {action}</div>
                <div class="action-text"><b>Expected Impact:</b> {impact}</div>
            </div>
            """
        )


# ============================================================
# MONGODB CONNECTION
# ============================================================

@st.cache_resource
def get_db():
    mongo_uri = st.secrets["MONGO_URI"]
    db_name = st.secrets.get("DB_NAME", "kayfa_student_analytics")

    client = MongoClient(
        mongo_uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=30000,
    )

    client.admin.command("ping")
    return client[db_name]


@st.cache_data(ttl=600, show_spinner=False)
def load_collection(collection_name):
    db = get_db()
    records = list(db[collection_name].find({}, {"_id": 0}))
    return pd.DataFrame(records)


def load_required(collection_name):
    try:
        df = load_collection(collection_name)
        return df
    except Exception as e:
        st.error(f"Failed to load collection '{collection_name}'")
        st.exception(e)
        return pd.DataFrame()


# ============================================================
# LOAD COLLECTIONS
# ============================================================

student_metrics = load_required("student_metrics")

if DEBUG_MONGO:
    try:
        db_debug = get_db()
        st.sidebar.error(f"Connected DB: {db_debug.name}")
        st.sidebar.error(f"Collections: {db_debug.list_collection_names()}")
        st.sidebar.error(
            f"student_metrics count: {db_debug['student_metrics'].count_documents({})}"
        )
    except Exception as e:
        st.sidebar.error("MongoDB debug failed")
        st.sidebar.exception(e)

course_priorities = load_required("course_priorities")
course_risk_summary = load_required("course_risk_summary")
course_risk_concentration = load_required("course_risk_concentration")
concept_priorities = load_required("concept_priorities")
student_priorities = load_required("student_priorities")
top_risk_students = load_required("top_risk_students")
risk_level_summary = load_required("risk_level_summary")
group_size_validation = load_required("group_size_validation")
student_segment_summary = load_required("student_segment_summary")
student_segments = load_required("student_segments")
instructor_summary = load_required("instructor_summary")
category_summary = load_required("category_summary")
difficulty_summary = load_required("difficulty_summary")
action_plan = load_required("action_plan")
cleaning_log_final = load_required("cleaning_log_final")

if student_metrics.empty:
    st.error("Collection 'student_metrics' is empty or missing. Check MongoDB upload and DB_NAME.")
    st.stop()


# ============================================================
# NUMERIC CLEANING
# ============================================================

student_metrics = to_numeric(
    student_metrics,
    [
        "attendance_rate",
        "attendance_rate_pct",
        "avg_grade",
        "risk_score",
        "late_submission_rate",
        "late_submission_rate_pct",
        "total_events",
        "active_days",
        "login_count",
        "video_watch_count",
        "resource_download_count",
        "forum_post_count",
        "quiz_attempt_count",
        "total_video_watch_hours",
        "unique_failed_concepts",
        "avg_buffer_hours",
        "avg_time_spent_minutes",
    ],
)

if "attendance_rate_pct" not in student_metrics.columns and "attendance_rate" in student_metrics.columns:
    student_metrics["attendance_rate_pct"] = student_metrics["attendance_rate"] * 100

if "late_submission_rate_pct" not in student_metrics.columns and "late_submission_rate" in student_metrics.columns:
    student_metrics["late_submission_rate_pct"] = student_metrics["late_submission_rate"] * 100

if "risk_level" not in student_metrics.columns and "risk_score" in student_metrics.columns:
    student_metrics["risk_level"] = pd.cut(
        student_metrics["risk_score"],
        bins=[-np.inf, 40, 60, 75, np.inf],
        labels=["Low Risk", "Medium Risk", "High Risk", "Critical Risk"],
    )

course_priorities = to_numeric(
    course_priorities,
    [
        "student_count",
        "avg_grade",
        "avg_attendance",
        "avg_risk_score",
        "High_or_Critical",
        "High_or_Critical_Rate",
        "priority_score",
    ],
)

course_risk_summary = to_numeric(
    course_risk_summary,
    [
        "student_count",
        "avg_grade",
        "avg_attendance",
        "avg_risk_score",
        "avg_late_rate",
        "avg_failed_concepts",
    ],
)

course_risk_concentration = to_numeric(
    course_risk_concentration,
    [
        "Low Risk",
        "Medium Risk",
        "High Risk",
        "Critical Risk",
        "High_or_Critical",
        "Total Students",
        "High_or_Critical_Rate",
    ],
)

concept_priorities = to_numeric(
    concept_priorities,
    [
        "total_attempts",
        "failed_attempts",
        "failure_rate_pct",
        "avg_score_pct",
        "concept_priority_score",
    ],
)

student_priorities = to_numeric(
    student_priorities,
    [
        "attendance_rate_pct",
        "avg_grade",
        "unique_failed_concepts",
        "late_submission_rate_pct",
        "risk_score",
    ],
)

top_risk_students = to_numeric(
    top_risk_students,
    [
        "attendance_rate_pct",
        "avg_grade",
        "unique_failed_concepts",
        "late_submission_rate_pct",
        "risk_score",
    ],
)

risk_level_summary = to_numeric(
    risk_level_summary,
    [
        "student_count",
        "avg_risk_score",
        "avg_grade",
        "avg_attendance",
        "avg_late_rate",
        "avg_failed_concepts",
    ],
)

group_size_validation = to_numeric(
    group_size_validation,
    [
        "stated_num_students",
        "actual_student_count",
        "size_difference",
        "absolute_difference",
    ],
)

student_segment_summary = to_numeric(
    student_segment_summary,
    [
        "student_count",
        "avg_grade",
        "avg_attendance",
        "avg_total_events",
        "avg_active_days",
        "avg_failed_concepts",
        "avg_late_rate",
        "avg_risk_score",
    ],
)

student_segments = to_numeric(
    student_segments,
    [
        "attendance_rate_pct",
        "avg_grade",
        "total_events",
        "active_days",
        "unique_failed_concepts",
        "late_submission_rate_pct",
        "risk_score",
    ],
)

instructor_summary = to_numeric(
    instructor_summary,
    [
        "student_count",
        "avg_grade",
        "avg_attendance",
        "avg_risk_score",
        "high_risk_students",
        "critical_risk_students",
        "high_or_critical_students",
        "high_or_critical_rate",
    ],
)

category_summary = to_numeric(
    category_summary,
    ["student_count", "avg_grade", "avg_attendance", "avg_risk_score"],
)

difficulty_summary = to_numeric(
    difficulty_summary,
    ["student_count", "avg_grade", "avg_attendance", "avg_risk_score"],
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:
    render_logo(width=165)

    st.markdown("## Filters")

    course_options = sorted(student_metrics["course_name"].dropna().unique().tolist())
    selected_courses = st.multiselect(
        "Courses",
        options=course_options,
        default=course_options,
    )

    risk_order = ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]
    existing_risks = student_metrics["risk_level"].dropna().astype(str).unique().tolist()
    risk_options = [r for r in risk_order if r in existing_risks]

    selected_risks = st.multiselect(
        "Risk Levels",
        options=risk_options,
        default=risk_options,
    )

    segment_options = []
    if "student_segment" in student_segments.columns:
        segment_options = sorted(student_segments["student_segment"].dropna().unique().tolist())

    selected_segments = st.multiselect(
        "Student Segments",
        options=segment_options,
        default=segment_options,
    )

    st.markdown("---")
    st.success("MongoDB Connected")
    st.caption("Database: kayfa_student_analytics")
    st.caption(f"Loaded Students: {len(student_metrics):,}")


filtered_students = student_metrics.copy()

if selected_courses:
    filtered_students = filtered_students[filtered_students["course_name"].isin(selected_courses)]

if selected_risks:
    filtered_students = filtered_students[filtered_students["risk_level"].astype(str).isin(selected_risks)]


filtered_segments = student_segments.copy()

if selected_courses and "course_name" in filtered_segments.columns:
    filtered_segments = filtered_segments[filtered_segments["course_name"].isin(selected_courses)]

if selected_segments and "student_segment" in filtered_segments.columns:
    filtered_segments = filtered_segments[filtered_segments["student_segment"].isin(selected_segments)]


# ============================================================
# HEADER
# ============================================================

logo_col, title_col = st.columns([1, 6])

with logo_col:
    render_logo(width=130)

with title_col:
    html(
        """
        <div class="hero">
            <div class="hero-title">Kayfa Student Analytics Command Center</div>
            <div class="hero-subtitle">
                Executive dashboard for student performance, attendance, engagement, risk concentration,
                concept mastery, learning segments, and intervention planning.
            </div>
        </div>
        """
    )


# ============================================================
# KPI OVERVIEW
# ============================================================

st.markdown("## Executive Overview")

total_students = len(filtered_students)
avg_grade = filtered_students["avg_grade"].mean()
avg_attendance = filtered_students["attendance_rate_pct"].mean()
avg_risk = filtered_students["risk_score"].mean()
high_critical_count = filtered_students["risk_level"].astype(str).isin(["High Risk", "Critical Risk"]).sum()
high_critical_rate = high_critical_count / total_students * 100 if total_students else 0

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    kpi_card("Total Students", f"{total_students:,}", "Filtered population")
with k2:
    kpi_card("Average Grade", fmt_pct(avg_grade), "Academic performance")
with k3:
    kpi_card("Average Attendance", fmt_pct(avg_attendance), "Attendance behavior")
with k4:
    kpi_card("Average Risk Score", fmt_num(avg_risk), "Overall risk index")
with k5:
    kpi_card("High/Critical Risk", f"{high_critical_count:,}", f"{high_critical_rate:.2f}% of students")


# ============================================================
# TABS
# ============================================================

tab_overview, tab_risk, tab_concepts, tab_behavior, tab_ops, tab_segments, tab_recs, tab_quality = st.tabs(
    [
        "Overview",
        "Risk",
        "Concepts",
        "Behavior",
        "Operations",
        "Segments",
        "Recommendations",
        "Data Quality",
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

with tab_overview:
    st.markdown("## Course Performance Overview")

    c1, c2 = st.columns(2)

    with c1:
        if not course_risk_summary.empty:
            df = course_risk_summary.sort_values("avg_grade", ascending=False)

            fig = px.bar(
                df,
                x="course_name",
                y="avg_grade",
                text="avg_grade",
                color="avg_grade",
                color_continuous_scale="Blues",
                title="Average Grade by Course",
                labels={"course_name": "Course", "avg_grade": "Average Grade (%)"},
                hover_name="course_name",
                hover_data={
                    "student_count": True,
                    "avg_attendance": ":.2f",
                    "avg_risk_score": ":.2f",
                    "avg_grade": ":.2f",
                },
            )

            fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig.update_layout(yaxis_range=[0, 100], xaxis_tickangle=-30, coloraxis_showscale=False)
            show_chart(style_fig(fig))

    with c2:
        if not course_risk_summary.empty:
            df = course_risk_summary.sort_values("avg_attendance", ascending=False)

            fig = px.bar(
                df,
                x="course_name",
                y="avg_attendance",
                text="avg_attendance",
                color="avg_attendance",
                color_continuous_scale="Blues",
                title="Average Attendance by Course",
                labels={"course_name": "Course", "avg_attendance": "Average Attendance (%)"},
                hover_name="course_name",
                hover_data={
                    "student_count": True,
                    "avg_grade": ":.2f",
                    "avg_risk_score": ":.2f",
                    "avg_attendance": ":.2f",
                },
            )

            fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig.update_layout(yaxis_range=[0, 100], xaxis_tickangle=-30, coloraxis_showscale=False)
            show_chart(style_fig(fig))

    if not course_risk_summary.empty:
        weakest_course = course_risk_summary.sort_values("avg_grade").iloc[0]
        insight(
            f"<b>{weakest_course['course_name']}</b> has the lowest average grade "
            f"at <b>{weakest_course['avg_grade']:.2f}%</b> and should be treated as a key performance concern."
        )
        recommendation(
            "Start with the weakest course for academic review, instructor follow-up, attendance support, and targeted learning sessions."
        )

    st.markdown("### Course Priority Score")

    if not course_priorities.empty:
        df = course_priorities.sort_values("priority_score", ascending=True)

        fig = px.bar(
            df,
            x="priority_score",
            y="course_name",
            orientation="h",
            text="priority_score",
            color="priority_score",
            color_continuous_scale="Blues",
            title="Final Course Intervention Priority",
            labels={"priority_score": "Priority Score", "course_name": "Course"},
            hover_name="course_name",
            hover_data={
                "student_count": True,
                "avg_grade": ":.2f",
                "avg_attendance": ":.2f",
                "High_or_Critical_Rate": ":.2f",
                "priority_score": ":.2f",
            },
        )

        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(coloraxis_showscale=False)
        show_chart(style_fig(fig, height=680))

        top_course = course_priorities.sort_values("priority_score", ascending=False).iloc[0]
        insight(
            f"<b>{top_course['course_name']}</b> is the highest intervention priority "
            f"with a priority score of <b>{top_course['priority_score']:.2f}</b>."
        )
        recommendation(
            "Use this priority score to decide where management, instructors, and advisors should focus first."
        )


# ============================================================
# RISK
# ============================================================

with tab_risk:
    st.markdown("## Risk Analysis")

    c1, c2 = st.columns(2)

    with c1:
        if not risk_level_summary.empty:
            fig = px.pie(
                risk_level_summary,
                names="risk_level",
                values="student_count",
                hole=0.55,
                title="Student Distribution by Risk Level",
                color_discrete_sequence=px.colors.sequential.Blues_r,
            )
            fig.update_traces(textinfo="label+percent+value", textfont_size=16)
            show_chart(style_fig(fig))

    with c2:
        if not course_risk_concentration.empty:
            df = course_risk_concentration.sort_values("High_or_Critical_Rate", ascending=False)

            fig = px.bar(
                df,
                x="course_name",
                y="High_or_Critical_Rate",
                text="High_or_Critical_Rate",
                color="High_or_Critical_Rate",
                color_continuous_scale="Blues",
                title="High/Critical Risk Rate by Course",
                labels={
                    "course_name": "Course",
                    "High_or_Critical_Rate": "High/Critical Risk Rate (%)",
                },
                hover_name="course_name",
                hover_data={
                    "Total Students": True,
                    "High Risk": True,
                    "Critical Risk": True,
                    "High_or_Critical": True,
                    "High_or_Critical_Rate": ":.2f",
                },
            )

            fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig.update_layout(yaxis_range=[0, 100], xaxis_tickangle=-30, coloraxis_showscale=False)
            show_chart(style_fig(fig))

    if not course_risk_concentration.empty:
        top_risk_course = course_risk_concentration.sort_values("High_or_Critical_Rate", ascending=False).iloc[0]
        insight(
            f"<b>{top_risk_course['course_name']}</b> has the highest High/Critical Risk concentration "
            f"at <b>{top_risk_course['High_or_Critical_Rate']:.2f}%</b>."
        )
        recommendation(
            "Create a course-level intervention plan for this course, including attendance follow-up, assignment support, and concept remediation."
        )

    st.markdown("### Highest-Risk Students")

    risk_students_chart = student_priorities.copy()
    if risk_students_chart.empty:
        risk_students_chart = top_risk_students.copy()

    if not risk_students_chart.empty:
        risk_students_chart = risk_students_chart.sort_values("risk_score", ascending=False).head(12)

        risk_students_chart["Student"] = (
            risk_students_chart["full_name"].astype(str)
            + " — "
            + risk_students_chart["course_name"].astype(str)
        )

        fig = px.bar(
            risk_students_chart.sort_values("risk_score", ascending=True),
            x="risk_score",
            y="Student",
            orientation="h",
            text="risk_score",
            color="risk_score",
            color_continuous_scale="Blues",
            title="Top 12 Students by Risk Score",
            labels={"risk_score": "Risk Score", "Student": "Student"},
            hover_name="Student",
            hover_data={
                "student_id": True,
                "attendance_rate_pct": ":.2f",
                "avg_grade": ":.2f",
                "late_submission_rate_pct": ":.2f",
                "unique_failed_concepts": ":.2f",
            },
        )

        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(xaxis_range=[0, 100], coloraxis_showscale=False)
        show_chart(style_fig(fig, height=760))

        highest_student = risk_students_chart.iloc[0]
        insight(
            f"The highest-risk student is <b>{highest_student['full_name']}</b> "
            f"from <b>{highest_student['course_name']}</b>, with a risk score of "
            f"<b>{highest_student['risk_score']:.2f}</b>."
        )
        recommendation(
            "Use this chart instead of student cards because it shows the highest-risk students clearly and supports faster comparison."
        )


# ============================================================
# CONCEPTS
# ============================================================

with tab_concepts:
    st.markdown("## Concept Mastery")

    if not concept_priorities.empty:
        df = concept_priorities.copy()
        df["Concept"] = df["concept_name"].astype(str) + " — " + df["course_name"].astype(str)
        df = df.sort_values("concept_priority_score", ascending=True)

        fig = px.bar(
            df,
            x="concept_priority_score",
            y="Concept",
            orientation="h",
            text="concept_priority_score",
            color="concept_priority_score",
            color_continuous_scale="Blues",
            title="Top Concept Intervention Priorities",
            labels={"concept_priority_score": "Concept Priority Score", "Concept": "Concept"},
            hover_name="Concept",
            hover_data={
                "total_attempts": True,
                "failed_attempts": True,
                "failure_rate_pct": ":.2f",
                "avg_score_pct": ":.2f",
                "concept_priority_score": ":.2f",
            },
        )

        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(coloraxis_showscale=False)
        show_chart(style_fig(fig, height=760))

        worst_concept = concept_priorities.sort_values("failure_rate_pct", ascending=False).iloc[0]
        insight(
            f"<b>{worst_concept['concept_name']}</b> in <b>{worst_concept['course_name']}</b> "
            f"is the weakest concept with a failure rate of <b>{worst_concept['failure_rate_pct']:.2f}%</b>."
        )
        recommendation(
            "Redesign this concept using simpler explanations, worked examples, short practice tasks, and revision sessions."
        )

    st.markdown("### Clear Concept Weakness Comparison")

    if not concept_priorities.empty:
        df = concept_priorities.copy()
        df["Concept"] = df["concept_name"].astype(str) + " — " + df["course_name"].astype(str)
        df = df.sort_values("failure_rate_pct", ascending=False).head(10)

        fig = px.bar(
            df.sort_values("failure_rate_pct", ascending=True),
            x="failure_rate_pct",
            y="Concept",
            orientation="h",
            text="failure_rate_pct",
            color="failure_rate_pct",
            color_continuous_scale="Blues",
            title="Top 10 Concepts by Failure Rate",
            labels={"failure_rate_pct": "Failure Rate (%)", "Concept": "Concept"},
            hover_name="Concept",
            hover_data={
                "total_attempts": True,
                "failed_attempts": True,
                "avg_score_pct": ":.2f",
                "concept_priority_score": ":.2f",
                "failure_rate_pct": ":.2f",
            },
        )

        fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig.update_layout(xaxis_range=[0, 100], coloraxis_showscale=False)
        show_chart(style_fig(fig, height=720))

        worst_concept = df.sort_values("failure_rate_pct", ascending=False).iloc[0]
        insight(
            f"<b>{worst_concept['concept_name']}</b> is the clearest weakness, with a failure rate of "
            f"<b>{worst_concept['failure_rate_pct']:.2f}%</b> and an average score of "
            f"<b>{worst_concept['avg_score_pct']:.2f}%</b>."
        )
        recommendation(
            "Prioritize the highest-failure concepts first. These concepts should receive extra tutorials, simplified explanations, and practice assessments."
        )

    st.markdown("### Failure Rate vs Average Score Side-by-Side")

    if not concept_priorities.empty:
        df = concept_priorities.copy()
        df["Concept"] = df["concept_name"].astype(str) + " — " + df["course_name"].astype(str)
        df = df.sort_values("failure_rate_pct", ascending=False).head(10)

        compare_df = df[["Concept", "failure_rate_pct", "avg_score_pct"]].copy()
        compare_df = compare_df.rename(
            columns={
                "failure_rate_pct": "Failure Rate (%)",
                "avg_score_pct": "Average Score (%)",
            }
        )

        compare_long = compare_df.melt(
            id_vars="Concept",
            var_name="Metric",
            value_name="Value",
        )

        fig = px.bar(
            compare_long,
            x="Value",
            y="Concept",
            color="Metric",
            orientation="h",
            barmode="group",
            text="Value",
            title="Failure Rate and Average Score Comparison",
            labels={"Value": "Percentage (%)", "Concept": "Concept", "Metric": "Metric"},
            hover_name="Concept",
        )

        fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig.update_layout(xaxis_range=[0, 100], yaxis={"categoryorder": "total ascending"})
        show_chart(style_fig(fig, height=760))

        insight(
            "This chart is easier to read than the scatter plot because it directly compares each concept’s failure rate against its average score."
        )
        recommendation(
            "Use this view in the presentation because it clearly shows which concepts are failing and whether their average scores are also weak."
        )


# ============================================================
# BEHAVIOR
# ============================================================

with tab_behavior:
    st.markdown("## Attendance, Engagement, and Submission Behavior")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Attendance Impact")

        df = filtered_students.dropna(subset=["attendance_rate_pct", "avg_grade"]).copy()

        if not df.empty:
            df["Attendance Level"] = pd.cut(
                df["attendance_rate_pct"],
                bins=[0, 60, 70, 80, 90, 100],
                labels=["Below 60%", "60% to 70%", "70% to 80%", "80% to 90%", "90% to 100%"],
                include_lowest=True,
            )

            summary = (
                df.groupby("Attendance Level", observed=False)
                .agg(Average_Grade=("avg_grade", "mean"), Student_Count=("avg_grade", "count"))
                .reset_index()
            )

            corr = df["attendance_rate_pct"].corr(df["avg_grade"])

            fig = px.bar(
                summary,
                x="Attendance Level",
                y="Average_Grade",
                text="Average_Grade",
                color="Average_Grade",
                color_continuous_scale="Blues",
                title="Average Grade by Attendance Level",
                labels={"Average_Grade": "Average Grade (%)", "Student_Count": "Student Count"},
                hover_data={"Student_Count": True, "Average_Grade": ":.2f"},
            )

            fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig.update_layout(yaxis_range=[0, 100], coloraxis_showscale=False)
            show_chart(style_fig(fig))

            insight(f"Attendance has a positive relationship with grades. The correlation is <b>{corr:.3f}</b>.")
            recommendation("Create alerts for students below 60% attendance and assign advisor follow-up.")

    with c2:
        st.markdown("### Late Submission Impact")

        df = filtered_students.dropna(subset=["late_submission_rate_pct", "avg_grade"]).copy()

        if not df.empty:
            df["Late Submission Level"] = pd.cut(
                df["late_submission_rate_pct"],
                bins=[-0.1, 0, 33.34, 66.67, 100],
                labels=["No Late Submissions", "Low Late Rate", "Medium Late Rate", "High Late Rate"],
                include_lowest=True,
            )

            summary = (
                df.groupby("Late Submission Level", observed=False)
                .agg(Average_Grade=("avg_grade", "mean"), Student_Count=("avg_grade", "count"))
                .reset_index()
            )

            corr = df["late_submission_rate_pct"].corr(df["avg_grade"])

            fig = px.bar(
                summary,
                x="Late Submission Level",
                y="Average_Grade",
                text="Average_Grade",
                color="Average_Grade",
                color_continuous_scale="Blues",
                title="Average Grade by Late Submission Level",
                labels={"Average_Grade": "Average Grade (%)", "Student_Count": "Student Count"},
                hover_data={"Student_Count": True, "Average_Grade": ":.2f"},
            )

            fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig.update_layout(yaxis_range=[0, 100], coloraxis_showscale=False)
            show_chart(style_fig(fig))

            insight(f"Late submissions have a negative relationship with grades. The correlation is <b>{corr:.3f}</b>.")
            recommendation("Use deadline reminders and follow-up workflows for students with repeated late submissions.")

    st.markdown("### Engagement Drivers")

    engagement_cols = {
        "total_events": "Total Events",
        "active_days": "Active Days",
        "login_count": "Login Count",
        "video_watch_count": "Video Watch Count",
        "resource_download_count": "Resource Downloads",
        "forum_post_count": "Forum Posts",
        "quiz_attempt_count": "Quiz Attempts",
        "total_video_watch_hours": "Video Watch Hours",
    }

    corr_rows = []

    for col, label in engagement_cols.items():
        if col in filtered_students.columns:
            sub = filtered_students[[col, "avg_grade"]].dropna()
            if len(sub) > 2:
                corr_rows.append(
                    {
                        "Engagement Metric": label,
                        "Correlation with Average Grade": sub[col].corr(sub["avg_grade"]),
                    }
                )

    corr_df = pd.DataFrame(corr_rows).dropna()

    if not corr_df.empty:
        corr_df = corr_df.sort_values("Correlation with Average Grade", ascending=True)

        fig = px.bar(
            corr_df,
            x="Correlation with Average Grade",
            y="Engagement Metric",
            orientation="h",
            text="Correlation with Average Grade",
            color="Correlation with Average Grade",
            color_continuous_scale="Blues",
            title="Engagement Metrics Linked to Average Grade",
            labels={
                "Correlation with Average Grade": "Correlation with Average Grade",
                "Engagement Metric": "Engagement Metric",
            },
        )

        fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        fig.update_layout(coloraxis_showscale=False)
        show_chart(style_fig(fig, height=700))

        strongest = corr_df.sort_values("Correlation with Average Grade", ascending=False).iloc[0]
        insight(
            f"The strongest engagement signal is <b>{strongest['Engagement Metric']}</b> "
            f"with a correlation of <b>{strongest['Correlation with Average Grade']:.3f}</b>."
        )
        recommendation("Increase platform activity through reminders, quizzes, learning resources, and guided weekly tasks.")


# ============================================================
# OPERATIONS
# ============================================================

with tab_ops:
    st.markdown("## Instructor and Group Operations")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Instructor Risk Comparison")

        if not instructor_summary.empty:
            df = instructor_summary.sort_values("high_or_critical_rate", ascending=True)

            fig = px.bar(
                df,
                x="high_or_critical_rate",
                y="instructor",
                orientation="h",
                text="high_or_critical_rate",
                color="high_or_critical_rate",
                color_continuous_scale="Blues",
                title="High/Critical Risk Rate by Instructor",
                labels={"high_or_critical_rate": "High/Critical Risk Rate (%)", "instructor": "Instructor"},
                hover_name="instructor",
                hover_data={
                    "student_count": True,
                    "avg_grade": ":.2f",
                    "avg_attendance": ":.2f",
                    "avg_risk_score": ":.2f",
                },
            )

            fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig.update_layout(xaxis_range=[0, 100], coloraxis_showscale=False)
            show_chart(style_fig(fig))

            top_inst = instructor_summary.sort_values("high_or_critical_rate", ascending=False).iloc[0]
            insight(
                f"<b>{top_inst['instructor']}</b> has the highest High/Critical Risk rate "
                f"at <b>{top_inst['high_or_critical_rate']:.2f}%</b>."
            )
            recommendation(
                "Review instructor groups carefully, but interpret results with course difficulty and assigned cohort context."
            )

    with c2:
        st.markdown("### Group Size Validation")

        if not group_size_validation.empty:
            df = group_size_validation.sort_values("absolute_difference", ascending=True)

            fig = px.bar(
                df,
                x="absolute_difference",
                y="group_name",
                orientation="h",
                text="absolute_difference",
                color="absolute_difference",
                color_continuous_scale="Blues",
                title="Group Size Discrepancy",
                labels={"absolute_difference": "Absolute Student Difference", "group_name": "Group"},
                hover_name="group_name",
                hover_data={
                    "course_name": True,
                    "stated_num_students": True,
                    "actual_student_count": True,
                    "size_difference": True,
                },
            )

            fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
            fig.update_layout(coloraxis_showscale=False)
            show_chart(style_fig(fig))

            top_group = group_size_validation.sort_values("absolute_difference", ascending=False).iloc[0]
            insight(
                f"<b>{top_group['group_name']}</b> has the largest group-size discrepancy "
                f"with <b>{top_group['absolute_difference']:.0f}</b> students difference."
            )
            recommendation("Reconcile stated group size with actual student records before operational planning.")

    st.markdown("### Category and Difficulty Risk")

    c3, c4 = st.columns(2)

    with c3:
        if not category_summary.empty:
            df = category_summary.sort_values("avg_risk_score", ascending=True)

            fig = px.bar(
                df,
                x="avg_risk_score",
                y="category",
                orientation="h",
                text="avg_risk_score",
                color="avg_risk_score",
                color_continuous_scale="Blues",
                title="Average Risk Score by Course Category",
                labels={"avg_risk_score": "Average Risk Score", "category": "Course Category"},
                hover_name="category",
                hover_data={
                    "student_count": True,
                    "avg_grade": ":.2f",
                    "avg_attendance": ":.2f",
                    "avg_risk_score": ":.2f",
                },
            )

            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig.update_layout(xaxis_range=[0, 100], coloraxis_showscale=False)
            show_chart(style_fig(fig))

    with c4:
        if not difficulty_summary.empty:
            df = difficulty_summary.sort_values("avg_risk_score", ascending=True)

            fig = px.bar(
                df,
                x="avg_risk_score",
                y="difficulty_level",
                orientation="h",
                text="avg_risk_score",
                color="avg_risk_score",
                color_continuous_scale="Blues",
                title="Average Risk Score by Difficulty Level",
                labels={"avg_risk_score": "Average Risk Score", "difficulty_level": "Difficulty Level"},
                hover_name="difficulty_level",
                hover_data={
                    "student_count": True,
                    "avg_grade": ":.2f",
                    "avg_attendance": ":.2f",
                    "avg_risk_score": ":.2f",
                },
            )

            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig.update_layout(xaxis_range=[0, 100], coloraxis_showscale=False)
            show_chart(style_fig(fig))

    if not category_summary.empty:
        top_cat = category_summary.sort_values("avg_risk_score", ascending=False).iloc[0]
        insight(
            f"<b>{top_cat['category']}</b> is the highest-risk category "
            f"with an average risk score of <b>{top_cat['avg_risk_score']:.2f}</b>."
        )
        recommendation("Use category-level monitoring to identify curriculum areas that need broader redesign.")


# ============================================================
# SEGMENTS
# ============================================================

with tab_segments:
    st.markdown("## Student Segmentation")

    c1, c2 = st.columns(2)

    with c1:
        if not student_segment_summary.empty:
            fig = px.bar(
                student_segment_summary,
                x="student_segment",
                y="student_count",
                text="student_count",
                color="avg_risk_score",
                color_continuous_scale="Blues",
                title="Student Count by Learning Segment",
                labels={
                    "student_segment": "Student Segment",
                    "student_count": "Student Count",
                    "avg_risk_score": "Average Risk Score",
                },
                hover_name="student_segment",
                hover_data={
                    "avg_grade": ":.2f",
                    "avg_attendance": ":.2f",
                    "avg_failed_concepts": ":.2f",
                    "avg_late_rate": ":.2f",
                    "avg_risk_score": ":.2f",
                },
            )

            fig.update_traces(textposition="outside")
            fig.update_layout(coloraxis_showscale=False)
            show_chart(style_fig(fig))

    with c2:
        if not student_segment_summary.empty:
            segment_profile = student_segment_summary[
                [
                    "student_segment",
                    "avg_grade",
                    "avg_attendance",
                    "avg_risk_score",
                    "avg_late_rate",
                    "avg_failed_concepts",
                ]
            ].copy()

            segment_profile = segment_profile.rename(
                columns={
                    "student_segment": "Student Segment",
                    "avg_grade": "Average Grade",
                    "avg_attendance": "Average Attendance",
                    "avg_risk_score": "Average Risk Score",
                    "avg_late_rate": "Average Late Rate",
                    "avg_failed_concepts": "Average Failed Concepts",
                }
            )

            long_profile = segment_profile.melt(
                id_vars="Student Segment",
                var_name="Metric",
                value_name="Value",
            )

            fig = px.bar(
                long_profile,
                x="Student Segment",
                y="Value",
                color="Metric",
                barmode="group",
                text="Value",
                title="Learning Segment Profile",
                labels={"Student Segment": "Student Segment", "Value": "Metric Value", "Metric": "Metric"},
            )

            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            show_chart(style_fig(fig, height=650))

    if not student_segment_summary.empty:
        risk_seg = student_segment_summary.sort_values("avg_risk_score", ascending=False).iloc[0]
        insight(
            f"<b>{risk_seg['student_segment']}</b> is the weakest learning segment "
            f"with an average risk score of <b>{risk_seg['avg_risk_score']:.2f}</b>."
        )
        recommendation(
            "Use separate intervention plans for each segment: enrichment for strong students, monitoring for developing students, and immediate support for at-risk students."
        )

    st.markdown("### Student Segment Mix by Course")

    if not filtered_segments.empty:
        segment_course_risk = (
            filtered_segments
            .groupby(["course_name", "student_segment"], observed=False)
            .agg(
                Student_Count=("student_id", "count"),
                Average_Risk_Score=("risk_score", "mean"),
                Average_Grade=("avg_grade", "mean"),
                Average_Attendance=("attendance_rate_pct", "mean"),
            )
            .reset_index()
        )

        segment_course_risk[
            ["Average_Risk_Score", "Average_Grade", "Average_Attendance"]
        ] = segment_course_risk[
            ["Average_Risk_Score", "Average_Grade", "Average_Attendance"]
        ].round(2)

        course_totals = (
            segment_course_risk
            .groupby("course_name")["Student_Count"]
            .sum()
            .reset_index()
            .rename(columns={"Student_Count": "Course_Total"})
        )

        segment_course_risk = segment_course_risk.merge(course_totals, on="course_name", how="left")

        segment_course_risk["Segment_Percentage"] = (
            segment_course_risk["Student_Count"]
            / segment_course_risk["Course_Total"]
            * 100
        ).round(2)

        fig = px.bar(
            segment_course_risk,
            x="Segment_Percentage",
            y="course_name",
            color="student_segment",
            orientation="h",
            text="Segment_Percentage",
            title="Student Segment Mix by Course (%)",
            labels={
                "Segment_Percentage": "Segment Share (%)",
                "course_name": "Course",
                "student_segment": "Student Segment",
            },
            hover_data={
                "Student_Count": True,
                "Course_Total": True,
                "Average_Risk_Score": ":.2f",
                "Average_Grade": ":.2f",
                "Average_Attendance": ":.2f",
            },
        )

        fig.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
        fig.update_layout(
            barmode="stack",
            xaxis_range=[0, 100],
            legend_title_text="Student Segment",
            yaxis_title="Course",
            xaxis_title="Segment Share (%)",
        )

        show_chart(style_fig(fig, height=720))

    st.markdown("### Highest-Risk Segment per Course")

    if not filtered_segments.empty:
        segment_course_risk = (
            filtered_segments
            .groupby(["course_name", "student_segment"], observed=False)
            .agg(
                Student_Count=("student_id", "count"),
                Average_Risk_Score=("risk_score", "mean"),
                Average_Grade=("avg_grade", "mean"),
                Average_Attendance=("attendance_rate_pct", "mean"),
            )
            .reset_index()
        )

        segment_course_risk[
            ["Average_Risk_Score", "Average_Grade", "Average_Attendance"]
        ] = segment_course_risk[
            ["Average_Risk_Score", "Average_Grade", "Average_Attendance"]
        ].round(2)

        highest_segment_per_course = (
            segment_course_risk
            .sort_values("Average_Risk_Score", ascending=False)
            .groupby("course_name", as_index=False)
            .first()
            .sort_values("Average_Risk_Score", ascending=True)
        )

        highest_segment_per_course["Course + Segment"] = (
            highest_segment_per_course["course_name"].astype(str)
            + " — "
            + highest_segment_per_course["student_segment"].astype(str)
        )

        fig = px.bar(
            highest_segment_per_course,
            x="Average_Risk_Score",
            y="Course + Segment",
            orientation="h",
            text="Average_Risk_Score",
            color="student_segment",
            title="Highest-Risk Segment Inside Each Course",
            labels={
                "Average_Risk_Score": "Average Risk Score",
                "Course + Segment": "Course and Segment",
                "student_segment": "Student Segment",
            },
            hover_data={
                "Student_Count": True,
                "Average_Grade": ":.2f",
                "Average_Attendance": ":.2f",
            },
        )

        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_layout(xaxis_range=[0, 100], legend_title_text="Student Segment")
        show_chart(style_fig(fig, height=720))

        highest_risk_segment = highest_segment_per_course.sort_values(
            "Average_Risk_Score",
            ascending=False,
        ).iloc[0]

        insight(
            f"The highest-risk course/segment combination is "
            f"<b>{highest_risk_segment['student_segment']}</b> in "
            f"<b>{highest_risk_segment['course_name']}</b>, with an average risk score of "
            f"<b>{highest_risk_segment['Average_Risk_Score']:.2f}</b>."
        )
        recommendation(
            "This chart is clearer than the heatmap because it shows only the most important risk segment inside each course."
        )


# ============================================================
# RECOMMENDATIONS
# ============================================================

with tab_recs:
    st.markdown("## Final Recommendations")

    render_action_cards(action_plan)

    final_recommendations = []

    if not course_priorities.empty:
        top_course = course_priorities.sort_values("priority_score", ascending=False).iloc[0]
        final_recommendations.append(
            f"Prioritize <b>{top_course['course_name']}</b> because it has the highest intervention priority score "
            f"(<b>{top_course['priority_score']:.2f}</b>)."
        )

    if not concept_priorities.empty:
        top_concept = concept_priorities.sort_values("failure_rate_pct", ascending=False).iloc[0]
        final_recommendations.append(
            f"Redesign <b>{top_concept['concept_name']}</b> in <b>{top_concept['course_name']}</b> because it has "
            f"the highest failure rate (<b>{top_concept['failure_rate_pct']:.2f}%</b>)."
        )

    if not student_segment_summary.empty:
        risk_segment = student_segment_summary.sort_values("avg_risk_score", ascending=False).iloc[0]
        final_recommendations.append(
            f"Monitor the <b>{risk_segment['student_segment']}</b> segment weekly because it has the highest average risk score "
            f"(<b>{risk_segment['avg_risk_score']:.2f}</b>)."
        )

    if not instructor_summary.empty:
        top_inst = instructor_summary.sort_values("high_or_critical_rate", ascending=False).iloc[0]
        final_recommendations.append(
            f"Review support needs for <b>{top_inst['instructor']}</b>, whose students show the highest High/Critical Risk rate "
            f"(<b>{top_inst['high_or_critical_rate']:.2f}%</b>)."
        )

    final_recommendations.append(
        "Create automated alerts for students below <b>60%</b> attendance and students with repeated late submissions."
    )

    final_recommendations.append(
        "Use the dashboard weekly to track whether risk concentration, failed concepts, attendance, and late submissions are improving."
    )

    st.markdown("### Most Important Recommendations")

    for i, rec in enumerate(final_recommendations, start=1):
        html(
            f"""
            <div class="final-rec">
                <b>{i}.</b> {rec}
            </div>
            """
        )


# ============================================================
# DATA QUALITY
# ============================================================

with tab_quality:
    st.markdown("## Data Quality Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        kpi_card("Cleaning Issues Logged", f"{len(cleaning_log_final):,}", "Final cleaning log")
    with c2:
        kpi_card("Validated Students", f"{len(student_metrics):,}", "Dashboard-ready students")
    with c3:
        kpi_card("Dashboard Collections", "16", "MongoDB analytical tables")

    cleaning_issue_count = len(cleaning_log_final)

    if "has_discrepancy" in group_size_validation.columns:
        discrepancy_count = (
            group_size_validation["has_discrepancy"]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes"])
            .sum()
        )
    else:
        discrepancy_count = 0

    quality_chart = pd.DataFrame(
        {
            "Quality Area": [
                "Cleaning Issues Logged",
                "Validated Students",
                "Group Size Discrepancies",
                "Dashboard Collections",
            ],
            "Count": [
                cleaning_issue_count,
                len(student_metrics),
                discrepancy_count,
                16,
            ],
        }
    )

    fig = px.bar(
        quality_chart,
        x="Quality Area",
        y="Count",
        text="Count",
        color="Count",
        color_continuous_scale="Blues",
        title="Data Quality and Validation Summary",
        labels={"Quality Area": "Quality Area", "Count": "Count"},
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-25)
    show_chart(style_fig(fig))

    insight(
        "The dataset was cleaned, validated across files, and transformed into dashboard-ready analytical tables."
    )
    recommendation(
        "Keep the cleaning log and validation outputs as part of the final submission to prove data quality work."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
html(
    """
    <div class="small-muted">
        Built for Kayfa Student Analytics • Streamlit + MongoDB Atlas • Dark Blue Executive Theme
    </div>
    """
)