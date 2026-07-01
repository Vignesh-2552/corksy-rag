export async function* parseSSEStream(
  response: Response,
): AsyncGenerator<string> {
  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Response body is not readable");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = line.slice(6);
      if (data === "[DONE]") return;
      if (data) yield data;
    }
  }

  if (buffer.startsWith("data: ")) {
    const data = buffer.slice(6);
    if (data && data !== "[DONE]") yield data;
  }
}
