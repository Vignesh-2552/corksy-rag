export interface AskRequest {
  question: string;
  session_id: string;
  top_k?: number;
}

export interface SourceReference {
  doc_id: string;
  source_file: string;
  score: number;
  snippet: string;
}

export interface AskResponse {
  answer: string;
  sources: SourceReference[];
  session_id: string;
}
