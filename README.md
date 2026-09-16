# Note2Flash

A Python and Flask flashcard prototype that turns a topic or study notes into question-and-answer cards using the OpenAI API. Choose 1–10 cards, generate a set, and click each card to reveal its answer.

Note2Flash is the original prototype preceding the broader StudyStack project.

## How it works

1. The browser sends a topic or notes and a card count to Flask.
2. The server validates the input before requesting flashcards from OpenAI.
3. The response is checked for valid JSON, the requested number of cards, and nonempty questions and answers.
4. Flask renders the cards; a small JavaScript function flips them in the browser.

HTML templates are in `templates/`, and the stylesheet is in `static/`. The API key stays on the server and is read from the environment.

## Local setup

Tested with Python 3.12 on Linux. Python 3.11–3.12 is the intended runtime range; dependencies are pinned in `requirements.txt`.

```bash
git clone https://github.com/Sarim-h191/Note2Flash.git
cd Note2Flash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. The homepage and styles load without an API key. Generating cards requires a key with access to the configured model and available API usage.

On Windows PowerShell, create the environment with `py -3.12 -m venv .venv` and activate it with `.venv\Scripts\Activate.ps1`. macOS and Windows execution have not been independently verified.

### Configure generation

Set `OPENAI_API_KEY` in the same terminal session before starting the app. For example, in macOS's default zsh, this prompts for the key without echoing it or putting its value in the command history:

```zsh
read -rs 'OPENAI_API_KEY?OpenAI API key: '
export OPENAI_API_KEY
python app.py
```

Keep the key private. Do not commit it to Git or put it in browser JavaScript. A `.env` file is not automatically loaded by this app. See the [OpenAI setup guide](https://developers.openai.com/api/docs/quickstart) for API credentials.

| Setting | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | Unset | Authorizes API requests |
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat Completions model supporting JSON output |
| `HOST` | `127.0.0.1` | Server bind address; use `0.0.0.0` for a remote preview |
| `PORT` | `5000` | Server port |

## Replit

Use a **new, separate import** of this repository to evaluate this version. Preserve any existing working Replit project, its configuration, and its secrets. Do not switch an existing project's branch or pull these changes into it as a setup step.

The included `.replit` file declares a Python runtime and starts `bash scripts/run_replit.sh`. The script creates a project-local virtual environment, installs the pinned dependencies into that environment, and starts Flask on `0.0.0.0:5000` with debugging disabled.

Add `OPENAI_API_KEY` privately through the new project's Secrets settings. If a manual workflow is needed, its shell command is:

```bash
bash scripts/run_replit.sh
```

This configuration is intended for a fresh import and has not yet been verified inside Replit. It is not a replacement for an older project's custom configuration. Replit's [configuration guide](https://docs.replit.com/features/project-setup/configuration) explains its runtime and run settings.

## Try it

Enter a short topic such as “Photosynthesis” and choose 3 cards. Generate the set and click each card to reveal its answer. Check the content against trusted study materials. To create a new set, use **Create More Flashcards**.

## Validation and error handling

- Notes must contain 1–10,000 characters after trimming whitespace.
- Card counts must be whole numbers from 1 to 10.
- Oversized requests are rejected before generation.
- Missing keys, rejected credentials, usage limits, connection failures, and malformed AI responses produce form errors rather than fake flashcards.
- The API client has a 30-second timeout and automatic retries disabled.
- Submitted notes are retained after ordinary validation or service errors.
- Rendered text is HTML-escaped by Jinja templates.

## Tests

```bash
python -m unittest -v
```

The tests require no API key and make no paid requests. They cover page/style loading, input limits, response validation, HTML escaping, and service failures. Integration tests exercise the real OpenAI SDK through an in-memory HTTP transport, including success, rejected credentials, usage limits, server failures, and timeouts.

See [verification notes](REPAIR_RESULTS.md) for what was checked and the remaining live-service verification boundary.

## Scope

This is a study prototype with no accounts, saved decks, database, or measured learning outcomes. Notes are sent to the configured OpenAI service for generation. Generated answers may be incorrect and should be reviewed. The included Flask server is for local development or a private preview; a public deployment would also need production hosting and controls against unwanted API usage.
