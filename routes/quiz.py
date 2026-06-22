import json
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.database import db, QuizResult
from services.openai_service import generate_quiz

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/quiz")
@login_required
def quiz():
    return render_template("quiz.html")

@quiz_bp.route("/quiz/generate", methods=["POST"])
@login_required
def generate():
    data = request.get_json()
    topic = data.get("topic", "")
    difficulty = data.get("difficulty", "medium")
    num_questions = int(data.get("num_questions", 5))
    quiz_type = data.get("quiz_type", "mcq")

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    result = generate_quiz(topic, difficulty, num_questions, quiz_type)

    try:
        # Clean up markdown code blocks if present
        clean = result.strip().strip("```json").strip("```").strip()
        quiz_data = json.loads(clean)
    except Exception:
        return jsonify({"error": "Failed to parse quiz. Try again.", "raw": result}), 500

    return jsonify(quiz_data)

@quiz_bp.route("/quiz/submit", methods=["POST"])
@login_required
def submit():
    data = request.get_json()
    topic = data.get("topic", "Unknown")
    score = data.get("score", 0)
    total = data.get("total", 0)
    difficulty = data.get("difficulty", "medium")

    result = QuizResult(
        user_id=current_user.id,
        topic=topic,
        score=score,
        total=total,
        difficulty=difficulty
    )
    db.session.add(result)
    db.session.commit()

    return jsonify({"status": "saved", "percentage": round((score / total) * 100) if total else 0})
