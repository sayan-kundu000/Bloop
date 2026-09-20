"""
Bloop Quantum Experiment Repository (SQLAlchemy 2.x)
Encapsulates data persistence and queries for Quantum Intelligence experiments.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from backend.app.models.quantum_experiment import QuantumExperiment


class QuantumExperimentRepository:
    """Repository handling persistence and queries for the Quantum Intelligence domain."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        experiment_type: str,
        title: str,
        input_payload: Dict[str, Any],
        results: Dict[str, Any],
        user_id: Optional[int] = None,
        qubit_count: int = 2,
        circuit_depth: int = 0,
        execution_time_ms: float = 0.0,
        simulator: str = "qiskit_aer",
        description: Optional[str] = None,
        status: str = "completed",
        error_code: Optional[str] = None,
    ) -> QuantumExperiment:
        exp = QuantumExperiment(
            user_id=user_id,
            experiment_type=experiment_type,
            title=title,
            description=description,
            status=status,
            input_payload=input_payload,
            results=results,
            qubit_count=qubit_count,
            circuit_depth=circuit_depth,
            execution_time_ms=execution_time_ms,
            simulator=simulator,
            error_code=error_code,
        )
        self.db.add(exp)
        self.db.commit()
        self.db.refresh(exp)
        return exp

    def list_recent(
        self,
        user_id: Optional[int] = None,
        experiment_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[QuantumExperiment]:
        stmt = select(QuantumExperiment)
        if user_id is not None:
            stmt = stmt.where(QuantumExperiment.user_id == user_id)
        if experiment_type:
            stmt = stmt.where(QuantumExperiment.experiment_type == experiment_type)
        stmt = stmt.order_by(desc(QuantumExperiment.created_at)).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(
        self,
        experiment_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[QuantumExperiment]:
        stmt = select(QuantumExperiment).where(QuantumExperiment.id == experiment_id)
        if user_id is not None:
            stmt = stmt.where(QuantumExperiment.user_id == user_id)
        return self.db.execute(stmt).scalars().first()
