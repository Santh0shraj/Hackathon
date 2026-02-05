# ORM models for workflows, runs, and other domain entities.

import enum
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class RunStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ContextStrategy(str, enum.Enum):
    full = "full"
    code_only = "code_only"
    summary = "summary"


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    steps = relationship("Step", back_populates="workflow", order_by="Step.step_order")
    runs = relationship("WorkflowRun", back_populates="workflow")

    def __repr__(self):
        return f"<Workflow(id={self.id}, name={repr(self.name)})>"


class Step(Base):
    __tablename__ = "steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    step_order = Column(Integer, nullable=False)
    model_name = Column(String(255), nullable=False)
    prompt_template = Column(Text, nullable=False)
    completion_type = Column(String(64), nullable=True)
    completion_value = Column(Text, nullable=True)
    retry_limit = Column(Integer, default=0, nullable=False)
    context_strategy = Column(
        Enum(ContextStrategy),
        default=ContextStrategy.full,
        nullable=False,
    )

    workflow = relationship("Workflow", back_populates="steps")
    step_runs = relationship("StepRun", back_populates="step")

    def __repr__(self):
        return f"<Step(id={self.id}, workflow_id={self.workflow_id}, step_order={self.step_order})>"


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(RunStatus), default=RunStatus.RUNNING, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)

    workflow = relationship("Workflow", back_populates="runs")
    step_runs = relationship("StepRun", back_populates="workflow_run")

    def __repr__(self):
        return f"<WorkflowRun(id={self.id}, workflow_id={self.workflow_id}, status={self.status})>"


class StepRun(Base):
    __tablename__ = "step_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_run_id = Column(
        Integer,
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_id = Column(Integer, ForeignKey("steps.id", ondelete="CASCADE"), nullable=False)
    attempt_number = Column(Integer, default=1, nullable=False)
    status = Column(Enum(RunStatus), default=RunStatus.RUNNING, nullable=False)
    llm_response = Column(LONGTEXT, nullable=True)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workflow_run = relationship("WorkflowRun", back_populates="step_runs")
    step = relationship("Step", back_populates="step_runs")

    def __repr__(self):
        return f"<StepRun(id={self.id}, workflow_run_id={self.workflow_run_id}, step_id={self.step_id}, status={self.status})>"
