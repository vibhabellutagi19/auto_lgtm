import os
from dataclasses import dataclass, field
from openai import OpenAI
import json
from loguru import logger
from .secret_service import SecretService

@dataclass
class LLMParameters:
    model: str = "gemini-2.0-flash"
    temperature: float = 0.2
    max_tokens: int = 8192
    chat_completion_choices: int = 1
    response_format: dict = field(default_factory=lambda: {"type": "json_object"})


class LLMService:
    def __init__(self, user_query: str, project_id: str):
        """
        Initialize LLM service with project ID for Secret Manager access.
        
        Args:
            user_query: The query to be processed by the LLM
            project_id: Google Cloud project ID for accessing secrets
        """
        self.secret_service = SecretService(project_id)
        self.api_key = self._get_api_key()
        self.client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=self.api_key,
        )
        self.user_query = user_query
        self.system_prompt = None
        self.messages = []

    def _get_api_key(self) -> str:
        """
        Get the Gemini API key from Secret Manager.
        
        Returns:
            The API key as a string
            
        Raises:
            ValueError: If the API key cannot be retrieved
        """
        try:
            api_key = self.secret_service.get_secret("gemini-api-key")
            if not api_key:
                raise ValueError("Failed to retrieve Gemini API key from Secret Manager")
            return api_key
        except Exception as e:
            logger.error(f"Error retrieving Gemini API key: {str(e)}")
            raise ValueError(f"Failed to retrieve Gemini API key: {str(e)}")

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt
        self.set_messages({"role": "system", "content": self.system_prompt})

    def set_messages(self, messages: dict):
        self.messages.append(messages)

    def generate_response(self, is_set_assistant_messages: bool = False):
        if not any(msg.get("role") == "user" for msg in self.messages):
            self.set_messages({"role": "user", "content": self.user_query})

        params = LLMParameters()

        response = self.client.chat.completions.create(
            model=params.model,
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            n=params.chat_completion_choices,
            response_format=params.response_format,
            messages=self.messages
        )

        content = response.choices[0].message.content
        if is_set_assistant_messages:
            self.set_messages({"role": "assistant", "content": json.dumps(self.response_to_json(content))})
            parsed_content = self.response_to_json(content)
            return parsed_content
        return content

    def response_to_json(self, content: str):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}

