import { apiFetch } from "@/lib/api/client";
import type { AskRequest, AskResponse } from "@/lib/api/types";
import { parseSSEStream } from "@/lib/sse";

export async function ask(request: AskRequest): Promise<AskResponse> {
  const response = await apiFetch("/api/v1/ask", {
    method: "POST",
    body: JSON.stringify(request),
  });
  return response.json() as Promise<AskResponse>;
}

export async function* askStream(
  request: AskRequest,
): AsyncGenerator<string> {
  const response = await apiFetch("/api/v1/ask/stream", {
    method: "POST",
    body: JSON.stringify(request),
  });
  yield* parseSSEStream(response);
}
