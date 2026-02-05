# Executes workflows: orchestrates steps and calls Unbound client as needed.

from datetime import datetime

from sqlalchemy.orm import Session

from .completion_checker import check_completion
from .unbound_client import call_llm

# Import from parent when run with backend as cwd or on path
try:
    from database import get_session
    from models import RunStatus, Step, StepRun, Workflow, WorkflowRun
except ImportError:
    from ..database import get_session
    from ..models import RunStatus, Step, StepRun, Workflow, WorkflowRun


def _build_prompt(prompt_template: str, previous_output: str) -> str:
    """Inject previous step output into the prompt template."""
    return prompt_template.replace("{previous_output}", previous_output)


def execute_workflow(workflow_id: int, session: Session | None = None) -> WorkflowRun:
    """
    Run a workflow synchronously: create run, execute steps in order with retries,
    log each attempt as StepRun, and set WorkflowRun status to SUCCESS or FAILED.

    If session is None, uses database.get_session() and commits on success.
    """
    if session is not None:
        return _execute_workflow(workflow_id, session)
    with get_session() as s:
        return _execute_workflow(workflow_id, s)


def _execute_workflow(workflow_id: int, session: Session) -> WorkflowRun:
    """Core execution logic; caller provides session and handles transaction."""
    workflow = session.get(Workflow, workflow_id)
    if workflow is None:
        raise ValueError(f"Workflow not found: {workflow_id}")

    run = WorkflowRun(workflow_id=workflow_id, status=RunStatus.RUNNING)
    session.add(run)
    session.flush()

    steps = (
        session.query(Step)
        .filter(Step.workflow_id == workflow_id)
        .order_by(Step.step_order)
        .all()
    )
    previous_output = ""

    for step in steps:
        max_attempts = 1 + (step.retry_limit or 0)
        step_succeeded = False

        for attempt in range(max_attempts):
            step_run = StepRun(
                workflow_run_id=run.id,
                step_id=step.id,
                attempt_number=attempt + 1,
                status=RunStatus.RUNNING,
            )
            session.add(step_run)
            session.flush()

            prompt = _build_prompt(step.prompt_template or "", previous_output)
            llm_result = call_llm(step.model_name, prompt)
            response_text = llm_result.response_text or ""

            completion_result = check_completion(
                response_text,
                step.completion_type or "",
                step.completion_value,
            )

            step_run.llm_response = response_text
            step_run.status = (
                RunStatus.SUCCESS if completion_result["success"] else RunStatus.FAILED
            )
            step_run.failure_reason = (
                None if completion_result["success"] else completion_result["reason"]
            )
            session.flush()

            if completion_result["success"]:
                previous_output = response_text
                step_succeeded = True
                break

        if not step_succeeded:
            run.status = RunStatus.FAILED
            run.finished_at = datetime.utcnow()
            session.flush()
            return run

    run.status = RunStatus.SUCCESS
    run.finished_at = datetime.utcnow()
    session.flush()
    return run
