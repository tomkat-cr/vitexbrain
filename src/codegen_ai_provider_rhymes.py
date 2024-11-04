
"""
Rhymes APIs
"""
import os
import time
import requests

from src.codegen_utilities import (
    log_debug,
    get_default_resultset,
)
from src.codegen_ai_provider_openai import get_openai_api_response
from src.codegen_ai_abstracts import LlmProviderAbstract

RHYMES_SUCCESS_RESPONSES = ["success", "Success", '成功']


class AriaLlm(LlmProviderAbstract):
    """
    Aria LLM class
    """
    def query(self, prompt: str, question: str,
              prompt_enhancement_text: str = None) -> dict:
        """
        Perform a Aria request
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
            "model": "aria",
            "api_key": os.environ.get("RHYMES_ARIA_API_KEY"),
            "base_url": "https://api.rhymes.ai/v1",
            "stop": ["<|im_end|>"],
            "messages": [
                {
                    "role": "user",
                    "content": prompt.format(question=question),
                },
            ],
            "temperature": 0.5,
            "top_p": 1,
            # "max_tokens": 2048,
        }

        # Get the OpenAI API response
        log_debug("aria_query | " +
                  f"model_params: {model_params}")
        response = get_openai_api_response(model_params)
        response['refined_prompt'] = refined_prompt

        log_debug("aria_query | " +
                  f"response: {response}")
        return response


class AllegroLlm(LlmProviderAbstract):
    """
    Allegro text-to-video LLM class
    """
    def request(self, question: str,
                prompt_enhancement_text: str = None) -> dict:
        """
        Perform a Allegro video generation request
        """
        return self.allegro_request_video(question, prompt_enhancement_text)

    def generation_check(
        self,
        request_response: dict,
        wait_time: int = 60
    ):
        """
        Perform a Allegro video generation request check
        """
        return self.allegro_check_video_generation(request_response, wait_time)

    def query(self, prompt: str, question: str,
              prompt_enhancement_text: str = None) -> dict:
        """
        Perform a Aria request
        """
        llm_model = AriaLlm({
            "provider": os.environ.get("LLM_PROVIDER"),
        })
        return llm_model.query(prompt, question,
                               prompt_enhancement_text)

    def allegro_query(self, model_params: dict) -> dict:
        """
        Perform a Allegro video generation request
        """
        response = get_default_resultset()
        headers = {
            "Authorization": f"{model_params.get('api_key')}",
            "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        }
        headers.update(model_params.get("headers", {}))
        query = model_params.get("query", {})
        payload = model_params.get("payload", {})
        rhymes_endpoint = model_params.get(
            "base_url", "https://api.rhymes.ai/v1/generateVideoSyn")

        query_string = "&".join([f"{key}={value}" for key, value
                                in query.items()])
        if query_string:
            api_url = f"{rhymes_endpoint}?{query_string}"
        else:
            api_url = rhymes_endpoint

        log_debug("allegro_query | " +
                  f"\nAPI URL: {api_url}" +
                  f"\nAPI headers: {headers}" +
                  f"\nAPI payload: {payload}"
                  f"\nAPI method: {model_params.get('method', 'POST')}")
        try:
            if model_params.get("method", "POST") == "POST":
                model_response = requests.post(
                    api_url, headers=headers,
                    json=payload)
            else:
                model_response = requests.get(api_url, headers=headers)
        except Exception as e:
            response['error'] = True
            response['error_message'] = str(e)
            return response

        if model_response.status_code != 200:
            response['error'] = True
            response['error_message'] = \
                "Request failed with status " \
                f"code {model_response.status_code}"
            return response

        log_debug("allegro_query | API response:" +
                  f"\n{model_response.json()}")
        response['response'] = model_response.json()
        return response

    def allegro_request_video(self, question: str,
                              prompt_enhancement_text: str):
        """
        Perform a Allegro video generation request
        """
        response = get_default_resultset()

        if prompt_enhancement_text:
            prompt_enhancer_result = self.prompt_enhancer(
                question, prompt_enhancement_text)
            if prompt_enhancer_result['error']:
                return prompt_enhancer_result
            refined_prompt = prompt_enhancer_result['response']
        else:
            refined_prompt = question

        rand_seed = int(time.time())
        model_params = {
            "api_key": os.environ.get("RHYMES_ALLEGRO_API_KEY"),
            "headers": {
                "Content-Type": "application/json",
            },
            "payload": {
                "refined_prompt": refined_prompt,
                "user_prompt": question,
                "num_step": 50,
                "rand_seed": rand_seed,
                "cfg_scale": 7.5,
            }
        }

        log_debug("allegro_request_video | GENERATE VIDEO | " +
                  f"model_params: {model_params}")

        response = self.allegro_query(model_params)
        response['refined_prompt'] = refined_prompt

        log_debug("allegro_request_video | GENERATION RESULT | " +
                  f"response: {response}")

        if response['error']:
            return response

        if (response["response"].get("message") and
           response["response"]['message'] not in RHYMES_SUCCESS_RESPONSES) \
           or not response["response"].get("data"):
            message = response["response"].get("message",
                                               "No message and no data")
            response['error'] = True
            response['error_message'] = message

        return response

    def allegro_check_video_generation(
        self,
        allegro_response: dict,
        wait_time: int = 60
    ):
        """
        Perform a Allegro video generation request check
        """
        request_id = allegro_response["response"]['data']
        log_debug("allegro_check_video_generation | " +
                  f"request_id: {request_id}")

        model_params = {
            "api_key": os.environ.get("RHYMES_ALLEGRO_API_KEY"),
            "base_url": 'https://api.rhymes.ai/v1/videoQuery',
            "query": {
                "requestId": request_id,
            },
            "method": "GET",
        }
        log_debug("allegro_check_video_generation | WAIT FOR VIDEO | " +
                  f"model_params: {model_params}")

        video_url = None
        for i in range(10):
            log_debug(f"allegro_check_video_generation | VERIFICATION TRY {i}")
            response = self.allegro_query(model_params)
            log_debug(f"allegro_check_video_generation | VERIFICATION {i} | " +
                      f"response: {response}")
            if response['error']:
                return response
            if response["response"]['message'] in RHYMES_SUCCESS_RESPONSES \
               and response["response"].get('data'):
                video_url = response["response"]['data']
                break
            time.sleep(wait_time)

        if not video_url:
            response["error"] = True
            response["error_message"] = \
                f"ERROR E-500: Video generation failed" \
                f" (request_id: {request_id}, response: {response})"

        response['video_url'] = video_url
        return response
