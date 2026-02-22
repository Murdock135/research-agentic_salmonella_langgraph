import unittest
from unittest.mock import patch, Mock
from langchain_aws import ChatBedrock

from sparq.utils.get_llm import get_llm
from sparq.settings import Settings


class TestGetLLM(unittest.TestCase):
    def setUp(self) -> None:
        s = Settings()
        s._load_env_variables()

    @patch('boto3.Session')
    def test_aws(self, mock_session):
        mock_session.return_value.client.return_value = Mock()

        model = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
        llm = get_llm(model=model, provider='aws_bedrock')
        self.assertIsInstance(llm, ChatBedrock)

