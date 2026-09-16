import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import app
import httpx
from openai import APIConnectionError, OpenAI


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


class SDKIntegrationTests(unittest.TestCase):
    """Exercise the real SDK against an in-memory HTTP service; no paid calls."""

    def client_factory(self, handler):
        def factory(**kwargs):
            return OpenAI(**kwargs, http_client=httpx.Client(transport=httpx.MockTransport(handler)))
        return factory

    def test_real_sdk_request_and_render(self):
        def handler(request):
            body = json.loads(request.content)
            self.assertEqual(request.url.path, '/v1/chat/completions')
            self.assertEqual(body['response_format'], {'type': 'json_object'})
            self.assertIn('exactly 3', body['messages'][1]['content'])
            return httpx.Response(200, json={
                'id': 'test-response', 'object': 'chat.completion', 'created': 0,
                'model': 'gpt-4o-mini',
                'choices': [{'index': 0, 'finish_reason': 'stop', 'message': {
                    'role': 'assistant', 'content': json.dumps({'flashcards': [
                        {'question': f'Question {i}', 'answer': f'Answer {i}'} for i in range(3)
                    ]})}}],
            })
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-placeholder'}), patch('app.OpenAI', side_effect=self.client_factory(handler)):
            response = app.app.test_client().post('/generate', data={'topic': 'World War II', 'num_cards': '3'})
            self.assertEqual(response.status_code, 200)
            for i in range(3):
                self.assertIn(f'Question {i}'.encode(), response.data)
                self.assertIn(f'Answer {i}'.encode(), response.data)

    def test_real_sdk_service_statuses(self):
        for status, expected in [(401, b'API key was rejected'), (429, b'rate or usage limit'), (500, b'could not complete')]:
            with self.subTest(status=status):
                def handler(request):
                    return httpx.Response(status, json={'error': {'message': 'private diagnostic', 'type': 'test_error'}})
                with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-placeholder'}), patch('app.OpenAI', side_effect=self.client_factory(handler)):
                    response = app.app.test_client().post('/generate', data={'topic': 'World War II'})
                    self.assertEqual(response.status_code, 503)
                    self.assertIn(expected, response.data)
                    self.assertNotIn(b'private diagnostic', response.data)
                    self.assertIn(b'World War II', response.data)

    def test_real_sdk_timeout(self):
        def handler(request):
            raise httpx.ReadTimeout('private timeout diagnostic', request=request)
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-placeholder'}), patch('app.OpenAI', side_effect=self.client_factory(handler)):
            response = app.app.test_client().post('/generate', data={'topic': 'cells'})
            self.assertEqual(response.status_code, 503)
            self.assertNotIn(b'private timeout diagnostic', response.data)


if __name__ == '__main__':
    unittest.main()
