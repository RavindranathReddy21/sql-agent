def test_get_schema():
    from app.nodes import get_schema
    from pydantic_models.agentState import AgentState

    state = AgentState(
        question="What is the total sales for each product?",
        db_schema="",
        sql_query="",
        result="",
        error="",
        attempts=0
    )

    updated_state = get_schema(state)
    assert updated_state.db_schema != ""
    print("Schema:", updated_state.db_schema)


if __name__ == "__main__":
    test_get_schema()
