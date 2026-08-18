from datetime import UTC, datetime

from aura.core.logger import logger
from aura.planning.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)
from aura.planning.priority import PriorityManager
from aura.planning.validator import PlanValidator


class Planner:
    def __init__(
        self,
        validator: PlanValidator | None = None,
        priority_manager: PriorityManager | None = None,
    ):
        self.validator = validator or PlanValidator()
        self.priority_manager = (
            priority_manager or PriorityManager()
        )

    def validate_plan(
        self,
        plan: Plan,
    ) -> None:
        self.validator.validate(plan)

    def create_plan(
        self,
        goal: str,
        metadata: dict | None = None,
    ) -> Plan:
        plan = Plan(
            goal=goal,
            metadata=metadata or {},
        )

        logger.info(
            "Created plan | id=%s | goal=%s",
            plan.id,
            plan.goal,
        )

        return plan

    def create_step(
        self,
        title: str,
        description: str = "",
        priority: int = 3,
        dependencies: list[str] | None = None,
        metadata: dict | None = None,
    ) -> PlanStep:
        self.priority_manager.validate_priority(
            priority
        )

        step = PlanStep(
            title=title,
            description=description,
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )

        logger.info(
            "Created plan step | "
            "id=%s | title=%s | priority=%s",
            step.id,
            step.title,
            step.priority,
        )

        return step

    def generate_plan(
        self,
        goal: str,
        metadata: dict | None = None,
    ) -> Plan:
        cleaned_goal = goal.strip()

        if not cleaned_goal:
            raise ValueError(
                "Goal cannot be empty."
            )

        plan = self.create_plan(
            goal=cleaned_goal,
            metadata=metadata,
        )

        generated_steps = (
            self._generate_steps_for_goal(
                cleaned_goal
            )
        )

        for step in generated_steps:
            self.add_step(
                plan,
                step,
            )

        self.validate_plan(plan)

        logger.info(
            "Generated structured plan | "
            "plan_id=%s | steps=%s",
            plan.id,
            len(plan.steps),
        )

        return plan

    def _generate_steps_for_goal(
        self,
        goal: str,
    ) -> list[PlanStep]:
        goal_lower = goal.lower()

        if self._is_research_goal(
            goal_lower
        ):
            return self._generate_research_steps(
                goal
            )

        if self._is_writing_goal(
            goal_lower
        ):
            return self._generate_writing_steps(
                goal
            )

        if self._is_api_goal(
            goal_lower
        ):
            return self._generate_api_steps(
                goal
            )

        if self._is_frontend_goal(
            goal_lower
        ):
            return self._generate_frontend_steps(
                goal
            )

        if self._is_mobile_goal(
            goal_lower
        ):
            return self._generate_mobile_steps(
                goal
            )

        if self._is_database_goal(
            goal_lower
        ):
            return self._generate_database_steps(
                goal
            )

        if self._is_software_goal(
            goal_lower
        ):
            return self._generate_software_steps(
                goal
            )

        return self._generate_general_steps(
            goal
        )

    def _is_api_goal(
        self,
        goal: str,
    ) -> bool:
        terms = {
            "api",
            "rest api",
            "restful api",
            "backend api",
            "fastapi",
            "endpoint",
            "endpoints",
        }

        return any(
            term in goal
            for term in terms
        )

    def _is_frontend_goal(
        self,
        goal: str,
    ) -> bool:
        terms = {
            "frontend",
            "front-end",
            "dashboard",
            "react website",
            "react app",
            "user interface",
            "ui website",
        }

        return any(
            term in goal
            for term in terms
        )

    def _is_mobile_goal(
        self,
        goal: str,
    ) -> bool:
        terms = {
            "mobile app",
            "android app",
            "ios app",
            "react native",
            "flutter",
        }

        return any(
            term in goal
            for term in terms
        )

    def _is_database_goal(
        self,
        goal: str,
    ) -> bool:
        terms = {
            "database",
            "sql database",
            "sqlite",
            "mysql",
            "postgresql",
            "schema",
        }

        return any(
            term in goal
            for term in terms
        )

    def _is_software_goal(
        self,
        goal: str,
    ) -> bool:
        terms = {
            "build",
            "develop",
            "create app",
            "create an app",
            "website",
            "web app",
            "web application",
            "software",
            "application",
            "system",
            "platform",
        }

        return any(
            term in goal
            for term in terms
        )

    def _is_research_goal(
        self,
        goal: str,
    ) -> bool:
        terms = {
            "research",
            "investigate",
            "analyze",
            "analyse",
            "compare",
            "study",
            "evaluate",
        }

        return any(
            term in goal
            for term in terms
        )

    def _is_writing_goal(
        self,
        goal: str,
    ) -> bool:
        terms = {
            "write",
            "draft",
            "compose",
            "prepare report",
            "create report",
            "document",
        }

        return any(
            term in goal
            for term in terms
        )

    def _generate_api_steps(
        self,
        goal: str,
    ) -> list[PlanStep]:
        first = self.create_step(
            title="Define API requirements",
            description=(
                f"Identify resources, operations, inputs, "
                f"outputs, and constraints for: {goal}"
            ),
            priority=5,
            metadata={
                "category": "analysis",
                "specialization": "api",
            },
        )

        second = self.create_step(
            title="Design data models",
            description=(
                "Define request models, response models, "
                "entities, and validation rules."
            ),
            priority=4,
            dependencies=[first.id],
            metadata={
                "category": "design",
                "specialization": "api",
            },
        )

        third = self.create_step(
            title="Design API endpoints",
            description=(
                "Define routes, HTTP methods, "
                "response codes, and endpoint behavior."
            ),
            priority=4,
            dependencies=[second.id],
            metadata={
                "category": "design",
                "specialization": "api",
            },
        )

        fourth = self.create_step(
            title="Implement API",
            description=(
                "Implement routes, business logic, "
                "validation, and persistence."
            ),
            priority=4,
            dependencies=[third.id],
            metadata={
                "category": "implementation",
                "specialization": "api",
            },
        )

        fifth = self.create_step(
            title="Test API",
            description=(
                "Test valid requests, invalid requests, "
                "edge cases, and endpoint responses."
            ),
            priority=3,
            dependencies=[fourth.id],
            metadata={
                "category": "testing",
                "specialization": "api",
            },
        )

        sixth = self.create_step(
            title="Document and finalize API",
            description=(
                "Review the API, resolve issues, "
                "and prepare documentation."
            ),
            priority=2,
            dependencies=[fifth.id],
            metadata={
                "category": "finalization",
                "specialization": "api",
            },
        )

        return [
            first,
            second,
            third,
            fourth,
            fifth,
            sixth,
        ]

    def _generate_frontend_steps(
        self,
        goal: str,
    ) -> list[PlanStep]:
        first = self.create_step(
            title="Define interface requirements",
            description=(
                f"Identify pages, components, states, "
                f"and interactions for: {goal}"
            ),
            priority=5,
            metadata={
                "category": "analysis",
                "specialization": "frontend",
            },
        )

        second = self.create_step(
            title="Design component structure",
            description=(
                "Define pages, reusable components, "
                "layouts, and application structure."
            ),
            priority=4,
            dependencies=[first.id],
            metadata={
                "category": "design",
                "specialization": "frontend",
            },
        )

        third = self.create_step(
            title="Implement user interface",
            description=(
                "Build responsive UI components "
                "and page layouts."
            ),
            priority=4,
            dependencies=[second.id],
            metadata={
                "category": "implementation",
                "specialization": "frontend",
            },
        )

        fourth = self.create_step(
            title="Add application behavior",
            description=(
                "Implement state, forms, navigation, "
                "events, and API integration."
            ),
            priority=4,
            dependencies=[third.id],
            metadata={
                "category": "implementation",
                "specialization": "frontend",
            },
        )

        fifth = self.create_step(
            title="Test interface",
            description=(
                "Verify responsiveness, validation, "
                "functionality, and UI states."
            ),
            priority=3,
            dependencies=[fourth.id],
            metadata={
                "category": "testing",
                "specialization": "frontend",
            },
        )

        return [
            first,
            second,
            third,
            fourth,
            fifth,
        ]

    def _generate_mobile_steps(
        self,
        goal: str,
    ) -> list[PlanStep]:
        first = self.create_step(
            title="Define mobile app requirements",
            description=(
                f"Identify screens, navigation, data, "
                f"and device requirements for: {goal}"
            ),
            priority=5,
            metadata={
                "category": "analysis",
                "specialization": "mobile",
            },
        )

        second = self.create_step(
            title="Design navigation flow",
            description=(
                "Define screens and navigation paths."
            ),
            priority=4,
            dependencies=[first.id],
            metadata={
                "category": "design",
                "specialization": "mobile",
            },
        )

        third = self.create_step(
            title="Build mobile screens",
            description=(
                "Implement reusable mobile components "
                "and application screens."
            ),
            priority=4,
            dependencies=[second.id],
            metadata={
                "category": "implementation",
                "specialization": "mobile",
            },
        )

        fourth = self.create_step(
            title="Implement mobile functionality",
            description=(
                "Add state, storage, API integration, "
                "and device-specific behavior."
            ),
            priority=4,
            dependencies=[third.id],
            metadata={
                "category": "implementation",
                "specialization": "mobile",
            },
        )

        fifth = self.create_step(
            title="Test mobile application",
            description=(
                "Verify navigation, behavior, "
                "screen states, and compatibility."
            ),
            priority=3,
            dependencies=[fourth.id],
            metadata={
                "category": "testing",
                "specialization": "mobile",
            },
        )

        return [
            first,
            second,
            third,
            fourth,
            fifth,
        ]

    def _generate_database_steps(
        self,
        goal: str,
    ) -> list[PlanStep]:
        first = self.create_step(
            title="Define data requirements",
            description=(
                f"Identify the data that must be stored "
                f"and retrieved for: {goal}"
            ),
            priority=5,
            metadata={
                "category": "analysis",
                "specialization": "database",
            },
        )

        second = self.create_step(
            title="Design database schema",
            description=(
                "Define tables, fields, relationships, "
                "constraints, and indexes."
            ),
            priority=4,
            dependencies=[first.id],
            metadata={
                "category": "design",
                "specialization": "database",
            },
        )

        third = self.create_step(
            title="Implement database",
            description=(
                "Create the schema and persistence operations."
            ),
            priority=4,
            dependencies=[second.id],
            metadata={
                "category": "implementation",
                "specialization": "database",
            },
        )

        fourth = self.create_step(
            title="Validate database operations",
            description=(
                "Test inserts, reads, updates, deletes, "
                "constraints, and data integrity."
            ),
            priority=3,
            dependencies=[third.id],
            metadata={
                "category": "testing",
                "specialization": "database",
            },
        )

        return [
            first,
            second,
            third,
            fourth,
        ]

    def _generate_software_steps(
        self,
        goal: str,
    ) -> list[PlanStep]:
        first = self.create_step(
            title="Understand requirements",
            description=(
                f"Clarify the requirements and expected "
                f"outcome for: {goal}"
            ),
            priority=5,
            metadata={
                "category": "analysis",
                "specialization": "software",
            },
        )

        second = self.create_step(
            title="Design solution",
            description=(
                "Define architecture, components, "
                "data flow, and technical approach."
            ),
            priority=4,
            dependencies=[first.id],
            metadata={
                "category": "design",
                "specialization": "software",
            },
        )

        third = self.create_step(
            title="Implement solution",
            description=(
                "Build the required software components."
            ),
            priority=4,
            dependencies=[second.id],
            metadata={
                "category": "implementation",
                "specialization": "software",
            },
        )

        fourth = self.create_step(
            title="Validate implementation",
            description=(
                "Run tests and verify the implementation."
            ),
            priority=3,
            dependencies=[third.id],
            metadata={
                "category": "testing",
                "specialization": "software",
            },
        )

        fifth = self.create_step(
            title="Finalize result",
            description=(
                "Resolve remaining issues and prepare "
                "the completed solution."
            ),
            priority=2,
            dependencies=[fourth.id],
            metadata={
                "category": "finalization",
                "specialization": "software",
            },
        )

        return [
            first,
            second,
            third,
            fourth,
            fifth,
        ]

    def _generate_research_steps(
        self,
        goal: str,
    ) -> list[PlanStep]:
        first = self.create_step(
            title="Define research objective",
            description=(
                f"Clarify the research question for: {goal}"
            ),
            priority=5,
            metadata={
                "category": "analysis",
            },
        )

        second = self.create_step(
            title="Gather information",
            description=(
                "Collect relevant information and evidence."
            ),
            priority=4,
            dependencies=[first.id],
            metadata={
                "category": "research",
            },
        )

        third = self.create_step(
            title="Analyze findings",
            description=(
                "Review and interpret the information."
            ),
            priority=4,
            dependencies=[second.id],
            metadata={
                "category": "analysis",
            },
        )

        fourth = self.create_step(
            title="Form conclusion",
            description=(
                "Produce conclusions supported "
                "by the findings."
            ),
            priority=3,
            dependencies=[third.id],
            metadata={
                "category": "conclusion",
            },
        )

        return [
            first,
            second,
            third,
            fourth,
        ]

    def _generate_writing_steps(
        self,
        goal: str,
    ) -> list[PlanStep]:
        first = self.create_step(
            title="Understand writing requirements",
            description=(
                f"Identify audience, purpose, and "
                f"requirements for: {goal}"
            ),
            priority=5,
            metadata={
                "category": "analysis",
            },
        )

        second = self.create_step(
            title="Create outline",
            description=(
                "Organize the structure and main ideas."
            ),
            priority=4,
            dependencies=[first.id],
            metadata={
                "category": "planning",
            },
        )

        third = self.create_step(
            title="Draft content",
            description=(
                "Produce the initial written version."
            ),
            priority=4,
            dependencies=[second.id],
            metadata={
                "category": "writing",
            },
        )

        fourth = self.create_step(
            title="Review and refine",
            description=(
                "Review clarity, correctness, "
                "completeness, and formatting."
            ),
            priority=3,
            dependencies=[third.id],
            metadata={
                "category": "review",
            },
        )

        return [
            first,
            second,
            third,
            fourth,
        ]

    def _generate_general_steps(
        self,
        goal: str,
    ) -> list[PlanStep]:
        first = self.create_step(
            title="Understand goal",
            description=(
                f"Clarify the desired outcome for: {goal}"
            ),
            priority=5,
            metadata={
                "category": "analysis",
            },
        )

        second = self.create_step(
            title="Prepare approach",
            description=(
                "Determine the best approach."
            ),
            priority=4,
            dependencies=[first.id],
            metadata={
                "category": "planning",
            },
        )

        third = self.create_step(
            title="Execute approach",
            description=(
                "Perform the required actions."
            ),
            priority=3,
            dependencies=[second.id],
            metadata={
                "category": "execution",
            },
        )

        fourth = self.create_step(
            title="Verify outcome",
            description=(
                "Verify successful completion."
            ),
            priority=2,
            dependencies=[third.id],
            metadata={
                "category": "verification",
            },
        )

        return [
            first,
            second,
            third,
            fourth,
        ]

    def add_step(
        self,
        plan: Plan,
        step: PlanStep,
    ) -> Plan:
        if any(
            existing_step.id == step.id
            for existing_step in plan.steps
        ):
            raise ValueError(
                f"Plan step '{step.id}' already exists."
            )

        plan.steps.append(step)
        plan.updated_at = datetime.now(UTC)

        return plan

    def remove_step(
        self,
        plan: Plan,
        step_id: str,
    ) -> Plan:
        step = self.get_step(
            plan,
            step_id,
        )

        if step is None:
            raise ValueError(
                f"Plan step '{step_id}' was not found."
            )

        dependent_steps = [
            candidate
            for candidate in plan.steps
            if step_id in candidate.dependencies
        ]

        if dependent_steps:
            raise ValueError(
                f"Cannot remove plan step '{step_id}' "
                "because other steps depend on it."
            )

        plan.steps = [
            candidate
            for candidate in plan.steps
            if candidate.id != step_id
        ]

        plan.updated_at = datetime.now(UTC)

        return plan

    def get_step(
        self,
        plan: Plan,
        step_id: str,
    ) -> PlanStep | None:
        for step in plan.steps:
            if step.id == step_id:
                return step

        return None

    def set_step_priority(
        self,
        plan: Plan,
        step_id: str,
        priority: int,
    ) -> PlanStep:
        self.priority_manager.validate_priority(
            priority
        )

        step = self.get_step(
            plan,
            step_id,
        )

        if step is None:
            raise ValueError(
                f"Plan step '{step_id}' was not found."
            )

        old_priority = step.priority

        step.priority = priority
        step.updated_at = datetime.now(UTC)

        plan.updated_at = datetime.now(UTC)

        logger.info(
            "Updated step priority | "
            "plan_id=%s | step_id=%s | "
            "old_priority=%s | new_priority=%s",
            plan.id,
            step.id,
            old_priority,
            priority,
        )

        return step

    def start_plan(
        self,
        plan: Plan,
    ) -> Plan:
        self.validate_plan(plan)

        plan.change_status(
            PlanStatus.IN_PROGRESS
        )

        self.refresh_step_readiness(
            plan
        )

        return plan

    def complete_plan(
        self,
        plan: Plan,
    ) -> Plan:
        incomplete_steps = [
            step
            for step in plan.steps
            if step.status
            not in {
                PlanStepStatus.COMPLETED,
                PlanStepStatus.SKIPPED,
            }
        ]

        if incomplete_steps:
            raise ValueError(
                "Cannot complete plan while "
                "unfinished steps remain."
            )

        plan.change_status(
            PlanStatus.COMPLETED
        )

        return plan

    def fail_plan(
        self,
        plan: Plan,
    ) -> Plan:
        plan.change_status(
            PlanStatus.FAILED
        )

        return plan

    def cancel_plan(
        self,
        plan: Plan,
    ) -> Plan:
        plan.change_status(
            PlanStatus.CANCELLED
        )

        return plan

    def refresh_step_readiness(
        self,
        plan: Plan,
    ) -> Plan:
        completed_ids = {
            step.id
            for step in plan.steps
            if step.status
            == PlanStepStatus.COMPLETED
        }

        for step in plan.steps:
            if (
                step.status
                != PlanStepStatus.PENDING
            ):
                continue

            dependencies_complete = all(
                dependency_id in completed_ids
                for dependency_id
                in step.dependencies
            )

            if dependencies_complete:
                step.change_status(
                    PlanStepStatus.READY
                )

        plan.updated_at = datetime.now(UTC)

        return plan

    def get_ready_steps(
        self,
        plan: Plan,
    ) -> list[PlanStep]:
        ready_steps = [
            step
            for step in plan.steps
            if step.status
            == PlanStepStatus.READY
        ]

        return self.priority_manager.sort_steps(
            ready_steps
        )

    def get_next_step(
        self,
        plan: Plan,
    ) -> PlanStep | None:
        ready_steps = self.get_ready_steps(
            plan
        )

        return self.priority_manager.select_next(
            ready_steps
        )

    def start_step(
        self,
        plan: Plan,
        step_id: str,
    ) -> PlanStep:
        step = self.get_step(
            plan,
            step_id,
        )

        if step is None:
            raise ValueError(
                f"Plan step '{step_id}' was not found."
            )

        step.change_status(
            PlanStepStatus.IN_PROGRESS
        )

        plan.updated_at = datetime.now(UTC)

        return step

    def complete_step(
        self,
        plan: Plan,
        step_id: str,
    ) -> PlanStep:
        step = self.get_step(
            plan,
            step_id,
        )

        if step is None:
            raise ValueError(
                f"Plan step '{step_id}' was not found."
            )

        step.change_status(
            PlanStepStatus.COMPLETED
        )

        plan.updated_at = datetime.now(UTC)

        self.refresh_step_readiness(
            plan
        )

        return step

    def fail_step(
        self,
        plan: Plan,
        step_id: str,
    ) -> PlanStep:
        step = self.get_step(
            plan,
            step_id,
        )

        if step is None:
            raise ValueError(
                f"Plan step '{step_id}' was not found."
            )

        step.change_status(
            PlanStepStatus.FAILED
        )

        plan.updated_at = datetime.now(UTC)

        return step

    def skip_step(
        self,
        plan: Plan,
        step_id: str,
    ) -> PlanStep:
        step = self.get_step(
            plan,
            step_id,
        )

        if step is None:
            raise ValueError(
                f"Plan step '{step_id}' was not found."
            )

        step.change_status(
            PlanStepStatus.SKIPPED
        )

        plan.updated_at = datetime.now(UTC)

        return step