from aura.planning.planner import Planner


def test_api_goal_generates_api_specific_steps():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a REST API for managing students."
    )

    titles = [
        step.title
        for step in plan.steps
    ]

    assert titles == [
        "Define API requirements",
        "Design data models",
        "Design API endpoints",
        "Implement API",
        "Test API",
        "Document and finalize API",
    ]


def test_frontend_goal_generates_frontend_steps():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a frontend dashboard."
    )

    titles = [
        step.title
        for step in plan.steps
    ]

    assert titles == [
        "Define interface requirements",
        "Design component structure",
        "Implement user interface",
        "Add application behavior",
        "Test interface",
    ]


def test_mobile_goal_generates_mobile_steps():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a React Native mobile app."
    )

    titles = [
        step.title
        for step in plan.steps
    ]

    assert titles == [
        "Define mobile app requirements",
        "Design navigation flow",
        "Build mobile screens",
        "Implement mobile functionality",
        "Test mobile application",
    ]


def test_database_goal_generates_database_steps():
    planner = Planner()

    plan = planner.generate_plan(
        "Create a MySQL database for a school system."
    )

    titles = [
        step.title
        for step in plan.steps
    ]

    assert titles == [
        "Define data requirements",
        "Design database schema",
        "Implement database",
        "Validate database operations",
    ]


def test_api_goal_has_api_specialization():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a FastAPI backend."
    )

    for step in plan.steps:
        assert (
            step.metadata["specialization"]
            == "api"
        )


def test_frontend_goal_has_frontend_specialization():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a frontend dashboard."
    )

    for step in plan.steps:
        assert (
            step.metadata["specialization"]
            == "frontend"
        )


def test_mobile_goal_has_mobile_specialization():
    planner = Planner()

    plan = planner.generate_plan(
        "Build an Android mobile app."
    )

    for step in plan.steps:
        assert (
            step.metadata["specialization"]
            == "mobile"
        )


def test_database_goal_has_database_specialization():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a PostgreSQL database."
    )

    for step in plan.steps:
        assert (
            step.metadata["specialization"]
            == "database"
        )


def test_api_dependencies_are_sequential():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a REST API."
    )

    assert plan.steps[0].dependencies == []

    for index in range(
        1,
        len(plan.steps),
    ):
        assert (
            plan.steps[index].dependencies
            == [
                plan.steps[index - 1].id
            ]
        )


def test_specialized_plan_can_start():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a frontend dashboard."
    )

    planner.start_plan(
        plan
    )

    assert (
        plan.steps[0].status.value
        == "ready"
    )

    assert (
        plan.steps[1].status.value
        == "pending"
    )