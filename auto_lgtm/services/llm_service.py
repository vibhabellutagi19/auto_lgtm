import os
from dataclasses import dataclass, field
from typing import Any, Dict, Union
from openai import OpenAI
import json
from loguru import logger
from .secret_service import SecretService

SECRET_ID = os.getenv("SECRET_ID")

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
        logger.info(f"LLMService initialized. API key present: {bool(self.api_key)}, key length: {len(self.api_key) if self.api_key else 0}")
        self.client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=self.api_key,
        )
        self.user_query = user_query
        self.system_prompt = None
        self.messages = []
        logger.debug(f"LLMService initialized with user_query: {user_query}")

    def _get_api_key(self) -> str:
        """
        Get the Gemini API key from secrets.
        
        Returns:
            The API key as a string
            
        Raises:
            ValueError: If the API key cannot be retrieved
        """
        try:
            key = self.secret_service.get_secret(SECRET_ID,"gemini_api_key")
            return key
        except Exception as e:
            logger.error(f"Error retrieving Gemini API key: {str(e)}")
            raise ValueError(f"Failed to retrieve Gemini API key: {str(e)}")

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt
        self.set_messages({"role": "system", "content": self.system_prompt})

    def set_messages(self, messages: dict):
        self.messages.append(messages)

    def generate_response(self) -> Union[Any, Dict[str, str]]:
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
        parsed_content = self.response_to_json(content)
        # TODO: Remove this once we have a better way to handle the response
        for comment in parsed_content:
            for key, value in comment.items():
                if key == "comment":
                    logger.debug(f"LLM review comments: {value}")
        return parsed_content

    def response_to_json(self, content: str):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from LLM.")
            return {"error": "Invalid JSON response"}

