from app.core.logger import get_logger
from app.agents.state import RAGState

log = get_logger("corksy.agents.execute_plan")


async def execute_plan(state: RAGState, retrieval_service, query_tool_service) -> RAGState:
    docs = list(state["retrieved_docs"])
    results = list(state["query_results"])

    for step in state["plan"]:
        log.info("[execute_plan] session=%s executing step=%s", state["session_id"], step["tool"])

        if step["tool"] == "search_documents":
            docs.extend(await retrieval_service.search(state["question"], state["top_k"]))

        elif step["tool"] == "run_query":
            try:
                result = await query_tool_service.run(step["query_name"], step["params"])
                results.append(
                    {"query_name": step["query_name"], "params": step["params"], "result": result, "error": None}
                )
            except Exception as exc:
                log.warning("[execute_plan] session=%s step failed: %s", state["session_id"], exc)
                results.append(
                    {"query_name": step["query_name"], "params": step["params"], "result": "", "error": str(exc)}
                )

        else:
            log.warning("[execute_plan] session=%s unknown tool '%s' — skipped", state["session_id"], step["tool"])

    log.info("[execute_plan] session=%s done — %d doc(s), %d query result(s)", state["session_id"], len(docs), len(results))
    return {**state, "retrieved_docs": docs, "query_results": results}
