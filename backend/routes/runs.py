# API routes for workflow runs (start run, get status, list runs, cancel).

from flask import Blueprint, jsonify

from database import get_session
from models import StepRun, WorkflowRun

runs_bp = Blueprint("runs", __name__)


def _step_run_to_json(sr: StepRun) -> dict:
    return {
        "id": sr.id,
        "workflow_run_id": sr.workflow_run_id,
        "step_id": sr.step_id,
        "attempt_number": sr.attempt_number,
        "status": sr.status.value if sr.status else None,
        "llm_response": sr.llm_response,
        "failure_reason": sr.failure_reason,
        "created_at": sr.created_at.isoformat() if sr.created_at else None,
    }


@runs_bp.route("/<int:run_id>", methods=["GET"])
def get_run(run_id: int):
    """GET /workflow-runs/<id> → fetch live execution status and logs."""
    with get_session() as session:
        run = session.get(WorkflowRun, run_id)
        if not run:
            return jsonify({"error": "workflow run not found"}), 404
        step_runs = (
            session.query(StepRun)
            .filter(StepRun.workflow_run_id == run_id)
            .order_by(StepRun.step_id, StepRun.attempt_number)
            .all()
        )
        return jsonify({
            "id": run.id,
            "workflow_id": run.workflow_id,
            "status": run.status.value if run.status else None,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "step_runs": [_step_run_to_json(sr) for sr in step_runs],
        })
