## ADDED Requirements

### Requirement: Accept multipart file uploads
The system SHALL expose a `POST /api/v1/upload` endpoint that accepts one or more files via `multipart/form-data` under the field name `files`.

#### Scenario: Single file upload
- **WHEN** a client sends a `POST /api/v1/upload` request with one PDF file
- **THEN** the system SHALL respond with HTTP 200 and a JSON body containing `status: "indexed"`, the filename, and the total chunk count

#### Scenario: Multiple files upload
- **WHEN** a client sends a `POST /api/v1/upload` request with multiple files of mixed types (PDF, TXT, CSV, JSON)
- **THEN** the system SHALL process all files, index all chunks, and return a single response listing all filenames and the combined chunk count

#### Scenario: Unsupported file type rejected
- **WHEN** a client uploads a file with an extension not in [.pdf, .txt, .json, .csv]
- **THEN** the system SHALL respond with HTTP 400 and a message listing the accepted file types

#### Scenario: File too large rejected
- **WHEN** a client uploads a file exceeding the configured `MAX_FILE_SIZE_MB` limit
- **THEN** the system SHALL respond with HTTP 413 before processing begins

### Requirement: Load documents by file type
The system SHALL select the correct LangChain document loader based on file extension.

#### Scenario: PDF file loaded
- **WHEN** the uploaded file has extension `.pdf`
- **THEN** the system SHALL use `PyPDFLoader` to extract text content

#### Scenario: TXT file loaded
- **WHEN** the uploaded file has extension `.txt`
- **THEN** the system SHALL use `TextLoader` to extract text content

#### Scenario: JSON file loaded
- **WHEN** the uploaded file has extension `.json`
- **THEN** the system SHALL use `JSONLoader` to extract text content

#### Scenario: CSV file loaded
- **WHEN** the uploaded file has extension `.csv`
- **THEN** the system SHALL use `CSVLoader` to extract text content

### Requirement: Chunk documents before indexing
The system SHALL split all loaded documents using `RecursiveCharacterTextSplitter` with `chunk_size=512` and `chunk_overlap=64` before embedding.

#### Scenario: Long document chunked
- **WHEN** a document's text exceeds 512 characters
- **THEN** the system SHALL produce multiple overlapping chunks rather than truncating

#### Scenario: Short document not over-chunked
- **WHEN** a document's text is shorter than 512 characters
- **THEN** the system SHALL produce a single chunk containing the full text

### Requirement: Embed chunks asynchronously
The system SHALL embed all chunks using OpenAI `text-embedding-3-small` in async batches of 100.

#### Scenario: Batch embedding
- **WHEN** more than 100 chunks are produced from uploaded files
- **THEN** the system SHALL embed them in batches of 100, awaiting each batch before the next

#### Scenario: Embedding failure propagated
- **WHEN** the OpenAI embeddings API returns an error
- **THEN** the system SHALL respond with HTTP 502 and not partially upsert to Qdrant

### Requirement: Upsert chunks into Qdrant documents collection
The system SHALL upsert all embedded chunks into the Qdrant collection named `documents` with the payload fields: `doc_id`, `source_file`, `chunk_index`, `text`, `indexed_at`.

#### Scenario: Successful upsert
- **WHEN** embedding completes without error
- **THEN** the system SHALL upsert all points to the `documents` collection and return a 200 response

#### Scenario: Qdrant unavailable
- **WHEN** the Qdrant client cannot reach the configured host
- **THEN** the system SHALL respond with HTTP 503 and a human-readable error message

### Requirement: Return indexed confirmation response
The system SHALL return a structured JSON response after successful indexing.

#### Scenario: Confirmation response shape
- **WHEN** one or more files are successfully indexed
- **THEN** the response SHALL contain `status` (string "indexed"), `files` (list of filenames), and `chunks` (integer total chunk count)
