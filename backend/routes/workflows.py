# API routes for workflow CRUD and listing (create, read, update, delete workflows).

from flask import Blueprint, request, jsonify

from database import get_session
from models import ContextStrategy, Step, Workflow
from services.workflow_executor import execute_workflow

workflows_bp = Blueprint("workflows", __name__)


def _workflow_to_json(w: Workflow) -> dict:
    return {
        "id": w.id,
        "name": w.name,
        "description": w.description,
        "created_at": w.created_at.isoformat() if w.created_at else None,
    }


def _step_to_json(s: Step) -> dict:
    return {
        "id": s.id,
        "workflow_id": s.workflow_id,
        "step_order": s.step_order,
        "model_name": s.model_name,
        "prompt_template": s.prompt_template,
        "completion_type": s.completion_type,
        "completion_value": s.completion_value,
        "retry_limit": s.retry_limit,
        "context_strategy": s.context_strategy.value if s.context_strategy else "full",
    }


@workflows_bp.route("", methods=["GET"])
def list_workflows():
    """GET /workflows → list all workflows."""
    with get_session() as session:
        workflows = session.query(Workflow).order_by(Workflow.id).all()
        return jsonify({"workflows": [_workflow_to_json(w) for w in workflows]})


@workflows_bp.route("", methods=["POST"])
def create_workflow():
    """POST /workflows → create a workflow."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400
    with get_session() as session:
        w = Workflow(name=name.strip(), description=data.get("description"))
        session.add(w)
        session.flush()
        return jsonify(_workflow_to_json(w)), 201


@workflows_bp.route("/<int:workflow_id>/steps", methods=["POST"])
def add_step(workflow_id: int):
    """POST /workflows/<id>/steps → add a step to the workflow."""
    with get_session() as session:
        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            return jsonify({"error": "workflow not found"}), 404
        data = request.get_json(silent=True) or {}
        step_order = data.get("step_order")
        model_name = data.get("model_name")
        prompt_template = data.get("prompt_template")
        if step_order is None or not model_name or prompt_template is None:
            return jsonify({"error": "step_order, model_name, and prompt_template are required"}), 400
        try:
            context_strategy = data.get("context_strategy", "full")
            if isinstance(context_strategy, str):
                context_strategy = ContextStrategy(context_strategy)
        except ValueError:
            return jsonify({"error": "context_strategy must be full, code_only, or summary"}), 400
        step = Step(
            workflow_id=workflow_id,
            step_order=int(step_order),
            model_name=model_name.strip(),
            prompt_template=prompt_template,
            completion_type=data.get("completion_type"),
            completion_value=data.get("completion_value"),
            retry_limit=int(data.get("retry_limit", 0)),
            context_strategy=context_strategy,
        )
        session.add(step)
        session.flush()
        return jsonify(_step_to_json(step)), 201


@workflows_bp.route("/<int:workflow_id>/run", methods=["POST"])
def run_workflow(workflow_id: int):
    """POST /workflows/<id>/run → execute the workflow (synchronous)."""
    with get_session() as session:
        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            return jsonify({"error": "workflow not found"}), 404
        try:
            run = execute_workflow(workflow_id, session=session)
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        return jsonify({
            "id": run.id,
            "workflow_id": run.workflow_id,
            "status": run.status.value,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        }), 201
