from agno.agent import Agent
from agno.models.groq import Groq
from agno.playground import Playground, serve_playground_app
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

# Usar ruta absoluta para la base de datos
agent_storage: str = "/app/tmp/agents.db"


web_agent = Agent(
    name="Web Agent",
    model=Groq(
        id="llama3-70b-8192",
        api_key="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",
    ),
    tools=[DuckDuckGoTools()],
    instructions=["Always include sources"],
    storage=SqliteStorage(table_name="web_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
)



finance_agent = Agent(
    name="William Cabrera",
    model=Groq(
        id="llama3-70b-8192",
        api_key="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",
    ),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)],
    instructions=["Always use tables to display data"],
    storage=SqliteStorage(table_name="finance_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
)



app = Playground(agents=[web_agent, finance_agent]).get_app()


# Add health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "agent-playground"}
    )


# Endpoint temporal para depuración de la base de datos con logs detallados
@app.get("/debug/db")
async def debug_db():
    import traceback
    db_path = "/app/tmp/agents.db"
    try:
        exists = os.path.exists(db_path)
        size = os.path.getsize(db_path) if exists else 0
        return JSONResponse({"db_exists": exists, "db_size": size, "cwd": os.getcwd()})
    except Exception as e:
        return JSONResponse({"error": str(e), "trace": traceback.format_exc(), "cwd": os.getcwd()}, status_code=500)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7777))
    serve_playground_app("playground:app", reload=False, port=port, host="0.0.0.0")