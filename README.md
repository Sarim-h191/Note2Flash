# Note2Flash

The original flashcard prototype that preceded the broader StudyStack project. A Python/Flask app sends a topic or notes to OpenAI and displays question-and-answer cards that can be flipped in the browser. Generated answers need review; study effectiveness has not been measured.

## Run locally (Python 3.11 or 3.12)

```bash
git clone https://github.com/Sarim-h191/Note2Flash.git
cd Note2Flash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export OPENAI_API_KEY='your-key-here'
python app.py
```

Open http://127.0.0.1:5000. In Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` and set the key in the current session with `$env:OPENAI_API_KEY='your-key-here'`.

The homepage works without a key. Generation requires a valid API key and available API usage. Never commit your key. The default model is `gpt-4o-mini`; `OPENAI_MODEL` can override it with a compatible Chat Completions model supporting JSON output. There is no database or saved-card feature.

## Repairs explained

- Flask looks in `templates/` for HTML and `static/` for CSS. Moving the files fixes missing-page and missing-style errors.
- The API client is created when generating cards, so missing configuration does not prevent the homepage from loading.
- Server-side checks reject blank notes, notes longer than 10,000 characters, and card counts outside 1–10. Browser checks alone can be bypassed.
- API failures appear as form errors, not fake flashcards. A timeout bounds the service wait; raw error details are not shown.
- JSON responses must contain the requested number of cards, each with nonempty question and answer strings. Truncated responses are rejected.
- Only Flask and the OpenAI SDK are needed. Unused machine-learning packages were removed.
- The local server uses localhost with debugging off by default.

## Tests

```bash
python -m unittest -v
```

Tests cover page/CSS loading without a key, invalid inputs, oversized requests, missing configuration, successful rendering and HTML escaping, malformed/truncated AI responses, and service failures. API responses are mocked: these tests make no paid requests and do not establish live generation quality.

## Short demo

1. Start the app and open the homepage.
2. Enter “Photosynthesis converts light energy into chemical energy. Chloroplasts contain chlorophyll.” Choose 3 cards.
3. Generate and click a card to reveal its answer. Check the answers against your notes.
4. Explain: “Flask receives the form, validates it, requests JSON flashcards, checks their structure, and renders them.”
5. If the API is unavailable, show the friendly error and describe the mocked tests honestly.
