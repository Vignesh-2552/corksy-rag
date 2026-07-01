from app.core.logger import get_logger

log = get_logger("corksy.query_tool")


class QueryToolService:
    """Executes a pre-approved query template, e.g. via corksy-support's /api/run-query.

    The transport (HTTP call with a service-scoped JWT vs. another integration
    path) hasn't been decided yet, so this raises instead of silently returning
    empty data. execute_plan catches the error per-step so a failed query
    doesn't take down document-only answers.
    """

    async def run(self, query_name: str, params: dict) -> str:
        log.warning("run_query('%s') requested but no corksy-support integration is wired", query_name)
        raise NotImplementedError(f"run_query('{query_name}') is not wired to corksy-support yet")
