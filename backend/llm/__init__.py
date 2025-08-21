"""Initializes LLM provider and client setup for the backend."""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from beeai_framework.backend import ChatModel, ChatModelParameters
from backend.llm.provider_type import LLMProviderType

load_dotenv()

LLM_PROVIDER = LLMProviderType(os.getenv("LLM_PROVIDER", LLMProviderType.OLLAMA.value))


def _get_model_parameters() -> Dict:
    parameters = {}
    if LLM_PROVIDER == LLMProviderType.OLLAMA:
        parameters = {
            "temperature": 0,
        }
    return parameters


def get_llm_client(
    model_name: str = "granite3.3:8b",
) -> Any:
    """
    Returns an LLM client based on the specified model name and provider type.
    :param model_name:
    :return:
    """
    model_parameters = _get_model_parameters()

    if LLM_PROVIDER == LLMProviderType.OLLAMA:
        return ChatModel.from_name(
            f"ollama:{model_name}", parameters=ChatModelParameters(**model_parameters)
        )
    return None
