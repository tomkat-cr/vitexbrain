"""
LLM provider abstract class
"""
from src.codegen_utilities import get_default_resultset
from src.codegen_utilities import log_debug
from src.codegen_ai_abstracts_constants import DEFAULT_PROMPT_ENHANCEMENT_TEXT


class LlmProviderAbstract:
    """
    Abstract class for LLM providers
    """
    def __init__(self, params: str):
        self.params = params
        self.provider = self.params.get("provider")
        self.api_key = self.params.get("api_key")
        self.model_name = self.params.get("model_name")

    def init_llm(self):
        """
        Abstract method for initializing the LLM
        """
        pass

    def query(self, prompt: str, question: str,
              prompt_enhancement_text: str = None) -> dict:
        """
        Abstract method for querying the LLM
        """
        raise NotImplementedError

    def request(self, question: str,
                prompt_enhancement_text: str = None) -> dict:
        """
        Abstract method for video or other llm/model type request
        """
        raise NotImplementedError

    def generation_check(
        self,
        request_response: dict,
        wait_time: int = 60
    ):
        """
        Perform a video or other llm/model type generation request check
        """
        raise NotImplementedError

    def prompt_enhancer(self, question: str,
                        prompt_enhancement_text: str = None) -> dict:
        """
        Perform a prompt enhancement request
        """
        response = get_default_resultset()
        if not prompt_enhancement_text:
            prompt_enhancement_text = DEFAULT_PROMPT_ENHANCEMENT_TEXT
        log_debug("PROMPT_ENHANCER | prompt_enhancement_text: " +
                  f"{prompt_enhancement_text}")
        llm_response = self.query(prompt_enhancement_text, question)
        log_debug("PROMPT_ENHANCER | llm_response: " + f"{llm_response}")
        if llm_response['error']:
            return llm_response
        refined_prompt = llm_response['response']
        # Clean the refined prompt
        refined_prompt = refined_prompt.replace("\n", " ")
        refined_prompt = refined_prompt.replace("\r", " ")
        refined_prompt = refined_prompt.replace("Refined Prompt:", "")
        refined_prompt = refined_prompt.strip()
        refined_prompt = refined_prompt.replace('"', '')
        response['response'] = refined_prompt
        return response
