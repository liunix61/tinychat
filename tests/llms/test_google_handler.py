import json
import unittest
from unittest.mock import MagicMock, Mock, patch

from tinychat.llms.google import GoogleAIHandler, GoogleAIClient


class TestGoogleGeminiHandler(unittest.TestCase):
    @patch.object(GoogleAIClient, "perform_chat_request")
    def test_get_response(self, mock_perform_chat_request):
        test_user_input = "hello Bard"
        test_model_response = "hello dear user"
        mock_perform_chat_request.return_value = test_model_response
        handler = GoogleAIHandler()
        response = handler.get_response(test_user_input)
        self.assertEqual(response, test_model_response)
        expected_messages = [
            {"parts": [{"text": test_user_input}], "role": "user"},
            {
                "parts": [{"text": test_model_response}],
                "role": "model",
            },
        ]
        self.assertEqual(handler._messages, expected_messages)


class TestGoogleGeminiHandlerStreaming(unittest.TestCase):
    @patch.object(GoogleAIClient, "perform_stream_request")
    def test_stream_response(self, mock_perform_stream_request):
        # Create a mock SSEClient with a mock events method
        mock_sse_client = MagicMock()
        mock_stream = iter(
            [
                Mock(
                    data=json.dumps(
                        {
                            "candidates": [
                                {"content": {"parts": [{"text": "response part 1"}]}}
                            ]
                        }
                    )
                ),
                Mock(
                    data=json.dumps(
                        {
                            "candidates": [
                                {"content": {"parts": [{"text": "response part 2"}]}}
                            ]
                        }
                    )
                ),
                Mock(data="[DONE]"),
            ]
        )
        mock_sse_client.events.return_value = mock_stream
        mock_perform_stream_request.return_value = mock_sse_client

        handler = GoogleAIHandler()
        generator = handler.stream_response("hello")

        # Extracting and verifying the stream response
        responses = []
        for part in generator:
            responses.append(part)

        self.assertEqual(responses, ["response part 1", "response part 2"])
        expected_messages = [
            {"parts": [{"text": "hello"}], "role": "user"},
            {"parts": [{"text": "response part 1response part 2"}], "role": "model"},
        ]
        self.assertEqual(handler._messages, expected_messages)
