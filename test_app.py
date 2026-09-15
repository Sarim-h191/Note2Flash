import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import app
from openai import APIConnectionError


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_home_and_css_without_key(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(self.client.get('/').status_code, 200)
            with self.client.get('/static/style.css') as response:
                self.assertEqual(response.status_code, 200)

    def test_invalid_input_never_calls_api(self):
        with patch('app.generate_flashcards') as generate:
            for data in ({'topic': ' '}, {'topic': 'x'*10001}, *({'topic': 'notes', 'num_cards': v} for v in ('0', '11', 'abc', '2.5'))):
                self.assertEqual(self.client.post('/generate', data=data).status_code, 400)
            generate.assert_not_called()

    def test_request_size_limit(self):
        self.assertEqual(self.client.post('/generate', data={'topic':'x'*70000}).status_code, 413)

    def test_missing_key(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.post('/generate', data={'topic': 'cells'})
            self.assertEqual(response.status_code, 503)
            self.assertIn(b'Set OPENAI_API_KEY', response.data)

    def fake_response(self, payload, finish='stop'):
        return SimpleNamespace(choices=[SimpleNamespace(finish_reason=finish, message=SimpleNamespace(content=payload))])

    def test_success_and_escaping(self):
        cards = [{'question': '<script>bad()</script>', 'answer': 'Answer'}]
        with patch.dict(os.environ, {'OPENAI_API_KEY':'test'}), patch('app.OpenAI') as cls:
            cls.return_value.__enter__.return_value.chat.completions.create.return_value = self.fake_response(json.dumps({'flashcards':cards}))
            response = self.client.post('/generate', data={'topic':'biology', 'num_cards':'1'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'&lt;script&gt;', response.data)
            self.assertNotIn(b'<script>bad()', response.data)

    def test_bad_model_responses(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY':'test'}), patch('app.OpenAI') as cls:
            create = cls.return_value.__enter__.return_value.chat.completions.create
            for payload in ('not json', '[]', '{}', '{"flashcards":[]}', '{"flashcards":[{"question":"Q","answer":""}]}'):
                create.return_value = self.fake_response(payload)
                with self.assertRaises(app.GenerationError):
                    app.generate_flashcards('biology', 1)
            create.return_value = self.fake_response('{"flashcards":[{"question":"Q","answer":"A"}]}', 'length')
            with self.assertRaises(app.GenerationError):
                app.generate_flashcards('biology', 1)

    def test_service_failure_is_safe(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY':'test'}), patch('app.OpenAI') as cls:
            cls.return_value.__enter__.return_value.chat.completions.create.side_effect = APIConnectionError(request=None, message='secret diagnostic')
            response = self.client.post('/generate', data={'topic':'biology'})
            self.assertEqual(response.status_code, 503)
            self.assertNotIn(b'secret diagnostic', response.data)


if __name__ == '__main__':
    unittest.main()
