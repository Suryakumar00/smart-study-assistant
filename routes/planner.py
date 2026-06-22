from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.database import db, StudyPlan
from services.openai_service import generate_study_plan

planner_bp = Blueprint("planner", __name__)

@planner_bp.route("/planner")
@login_required
def planner():
    plans = StudyPlan.query.filter_by(user_id=current_user.id).order_by(StudyPlan.created_at.desc()).all()
    return render_template("planner.html", plans=plans)

@planner_bp.route("/planner/generate", methods=["POST"])
@login_required
def generate():
    data = request.get_json()
    subject = data.get("subject", "")
    syllabus = data.get("syllabus", "")
    deadline = data.get("deadline", "")
    hours_per_day = data.get("hours_per_day", 2)

    if not subject:
        return jsonify({"error": "Subject is required"}), 400

    plan_content = generate_study_plan(subject, syllabus, deadline, hours_per_day)

    plan = StudyPlan(
        user_id=current_user.id,
        subject=subject,
        plan_content=plan_content,
        deadline=deadline
    )
    db.session.add(plan)
    db.session.commit()

    return jsonify({"plan": plan_content, "plan_id": plan.id})

@planner_bp.route("/planner/delete/<int:plan_id>", methods=["POST"])
@login_required
def delete_plan(plan_id):
    plan = StudyPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    db.session.delete(plan)
    db.session.commit()
    return jsonify({"status": "deleted"})
