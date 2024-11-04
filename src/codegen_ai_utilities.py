"""
AI utilities
"""
from src.codegen_ai_abstracts import LlmProviderAbstract
from src.codegen_ai_provider_rhymes import AriaLlm, AllegroLlm
from src.codegen_ai_provider_openai import OpenaiLlm


class LlmProvider(LlmProviderAbstract):
    """
    Abstract class for LLM providers
    """
    def __init__(self, params: str):
        self.params = params
        self.llm = None
        if self.params.get("provider") == "rhymes":
            self.llm = AriaLlm(self.params)
        elif self.params.get("provider") == "openai":
            self.llm = OpenaiLlm(self.params)
        else:
            raise ValueError("Invalid LLM provider")
        self.init_llm()

    def query(self, prompt: str, question: str,
              prompt_enhancement_text: str = None) -> dict:
        """
        Abstract method for querying the LLM
        """
        llm_response = self.llm.query(
            prompt, question,
            prompt_enhancement_text)
        return llm_response


class TextToVideoProvider(LlmProviderAbstract):
    """
    Abstract class for text-to-video providers
    """
    def __init__(self, params: str):
        self.params = params
        self.llm = None
        if self.params.get("provider") == "rhymes":
            self.llm = AllegroLlm(self.params)
        elif self.params.get("provider") == "openai":
            raise NotImplementedError
        else:
            raise ValueError("Invalid LLM provider")
        self.init_llm()

    def query(self, prompt: str, question: str,
              prompt_enhancement_text: str = None) -> dict:
        """
        Perform a LLM query request
        """
        return self.llm.query(
            prompt, question,
            prompt_enhancement_text)

    def request(self, question: str,
                prompt_enhancement_text: str = None) -> dict:
        """
        Perform a video generation request
        """
        return self.llm.request(question, prompt_enhancement_text)

    def generation_check(
        self,
        request_response: dict,
        wait_time: int = 60
    ):
        """
        Perform a video generation request check
        """
        return self.llm.generation_check(request_response, wait_time)
