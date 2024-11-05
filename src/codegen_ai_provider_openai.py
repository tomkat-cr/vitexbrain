"""
OpenAI API
"""
import os
from openai import OpenAI

from src.codegen_utilities import (
    log_debug,
    get_default_resultset,
)
from src.codegen_ai_abstracts import LlmProviderAbstract


def get_openai_api_response(model_params: dict) -> dict:
    """
    Returns the OpenAI API response for a LLM request
    """
    response = get_default_resultset()
    naming = {
        "model_name": "model",
    }
    # Initialize the OpenAI client
    client_config = {}
    for key in ["base_url", "api_key"]:
        if model_params.get(key):
            client_config[naming.get(key, key)] = model_params[key]
    try:
        client = OpenAI(**client_config)
    except Exception as e:
        response['error'] = True
        response['error_message'] = str(e)
        return response
    # Prepare the OpenAI API request
    model_config = {}
    for key in ["model", "model_name", "messages", "stop"]:
        if model_params.get(key):
            model_config[naming.get(key, key)] = model_params[key]
    for key in ["temperature"]:
        if model_params.get(key):
            model_config[naming.get(key, key)] = float(model_params[key])
    for key in ["top_p", "max_tokens"]:
        if model_params.get(key):
            model_config[naming.get(key, key)] = int(model_params[key])
    # Process the question and text
    llm_response = client.chat.completions.create(**model_config)
    # log_debug("get_openai_api_response | " +
    #           f"{model_params.get('provider', 'N/A')} " +
    #           f" LLM response: {llm_response}")
    try:
        response['response'] = llm_response.choices[0].message.content
    except Exception as e:
        response['error'] = True
        response['error_message'] = str(e)
    return response


class OpenaiLlm(LlmProviderAbstract):
    """
    OpenAI LLM class
    """
    def query(self, prompt: str, question: str,
              prompt_enhancement_text: str = None) -> dict:
        """
        Perform a OpenAI request
        """
        refined_prompt = None
        if prompt_enhancement_text:
            llm_response = self.prompt_enhancer(
                question, prompt_enhancement_text)
            if llm_response['error']:
                return llm_response
            refined_prompt = llm_response['response']
            prompt = refined_prompt

        model_params = {
            "provider": self.provider,
            "model": self.model_name,
            "api_key": self.api_key or os.environ.get("OPENAI_API_KEY"),
            "messages": [
                {
                    "role": "user",
                    "content": prompt.format(question=question),
                },
            ],
            "temperature": self.params.get("temperature", 0.5),
            "top_p": self.params.get("top_p", 1),
            "max_tokens": self.params.get("max_tokens"),
        }

        # Get the OpenAI API response
        log_debug("openai_query | " +
                  f"model_params: {model_params}")
        response = get_openai_api_response(model_params)
        response['refined_prompt'] = refined_prompt
        log_debug("openai_query | " +
                  f"response: {response}")
        return response
