"""
LLM provider abstract class
"""
from src.codegen_utilities import get_default_resultset
from src.codegen_utilities import log_debug

# Avoid flake8 and pylint errors for long lines
# flake8: noqa
# pylint: disable=line-too-long

DEFAULT_PROMPT_ENHANCEMENT_TEXT = """
Improve the given initial prompt to make it clearer, more effective, and aligned with the task objectives and expectations.

# Steps

1. Carefully review the initial prompt provided.
2. Identify unclear instructions, missing details, or any ambiguity that could affect the model’s performance.
3. Add specific guidelines, necessary context, or well-defined examples if needed.
4. Make sure the prompt provides a clear and straightforward reasoning process before concluding the answer. 
5. Ensure the expected output is explicitly defined, including format, structure, and requirements.
6. Avoid unnecessary complexity—focus on simplicity, clarity, and effectiveness.

# Output Format

An enhanced version of the prompt with:
- Clarity in language and expectations
- Structured reasoning before conclusions
- Defined output format for consistency.

# Example

**Initial Prompt (Input)**:  
"Explain why a tomato is a fruit, and then list some related fruits."

**Enhanced Prompt (Output)**:  
"Explain step-by-step why a tomato is scientifically classified as a fruit. Start by describing the botanical characteristics that belong to fruits. After explaining, provide a list of other fruits that share similar characteristics as a tomato, such as being soft and containing seeds."

### Notes:
- When enhancing the prompt, ensure reasoning precedes any conclusion or answer.
- Always define how the output should be structured (e.g., format length or elements).
"""


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

        response = allegro_(
            question,
            (REFINE_VIDEO_PROMPT_TEXT if
             st.session_state.prompt_enhancement_flag else None)
        )

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
