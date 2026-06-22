from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models.database import QuizResult
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@dashboard_bp.route("/dashboard/data")
@login_required
def data():
    results = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.created_at).all()

    total_quizzes = len(results)
    avg_score = 0
    topic_performance = {}
    scores_over_time = []

    for r in results:
        pct = round((r.score / r.total) * 100) if r.total else 0
        avg_score += pct
        scores_over_time.append({
            "date": r.created_at.strftime("%b %d"),
            "score": pct,
            "topic": r.topic
        })
        if r.topic not in topic_performance:
            topic_performance[r.topic] = {"total": 0, "count": 0}
        topic_performance[r.topic]["total"] += pct
        topic_performance[r.topic]["count"] += 1

    avg_score = round(avg_score / total_quizzes) if total_quizzes else 0

    # Weak topics = avg score < 60
    weak_topics = [t for t, v in topic_performance.items() if (v["total"] / v["count"]) < 60]

    topic_labels = list(topic_performance.keys())
    topic_scores = [round(v["total"] / v["count"]) for v in topic_performance.values()]

    return jsonify({
        "total_quizzes": total_quizzes,
        "avg_score": avg_score,
        "weak_topics": weak_topics,
        "scores_over_time": scores_over_time,
        "topic_labels": topic_labels,
        "topic_scores": topic_scores
    })
