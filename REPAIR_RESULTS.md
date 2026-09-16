# Verification notes

## Repository checks

The release is tested independently of the original Replit workspace using Python 3.12, Flask 3.1.3, and OpenAI SDK 2.54.0. The Flask templates and static files are included in their expected directories. Dependencies are installed from the pinned requirements file.

All 10 automated tests passed. The test suite covers homepage and CSS loading without credentials, invalid input rejected before API calls, request-size limits, missing keys, valid rendering, escaped HTML, malformed/truncated responses, safe service errors, and the real SDK's request/response handling through an in-memory HTTP transport.

The startup script was also executed from an empty project-local virtual environment on Linux. It installed the pinned dependencies, started Flask on the configured port, served the homepage and stylesheet over HTTP, and returned the expected form error when no API key was configured. Dependency checks and shell syntax checks passed.

## Live-service boundary

No live OpenAI request has been made from this revised repository during release verification. Mocked tests establish request handling and rendering, not live model availability or flashcard accuracy.

The original Replit application was separately confirmed to generate World War II flashcards before this release. That observation does not constitute a live test of this revision. The original workspace is preserved separately and is not modified by the release procedure.

## Replit configuration

The repository includes an explicit runtime declaration and startup script for a fresh, separate Replit import. The script installs dependencies into a local virtual environment before starting the server. Replit provisioning and its Preview UI remain unverified until tested in a separate project. Existing working Replit projects should keep their own configuration.
