import os
import time
import json

from dotenv import load_dotenv
import requests
import uuid
import streamlit as st
from openai import OpenAI


DEBUG = True
REFINE_VIDEO_PROMPT = False
CONVERSATION_DB_PATH = "./db/conversations.json"
CONVERSATION_LENGTH = 50
DEFAULT_SUGGESTIONS = {
    "s1": "Step-by-step tutorial to make tea, presented in an animated"
    " format",
    "s2": "Landscape photography of a mountain in the Swiss Alps",
    "s3": "Give me ideas for the summer vacation in Hawaii",
    "s4": "Give me the ReactJs code for a AI Assistant,"
          " using Shadcn/UI",
}


# General utilities


def log_debug(message) -> None:
    """
    Log a debug message if the DEBUG flag is set to True
    """
    if DEBUG:
        print("")
        print(f"DEBUG {time.strftime('%Y-%m-%d %H:%M:%S')}: {message}")


def get_default_resultset() -> dict:
    """
    Returns a default resultset
    """
    return {
        "resultset": {},
        "error_message": "",
        "error": False,
    }


def get_date_time(timestamp: int):
    return time.strftime("%Y-%m-%d %H:%M:%S",
                         time.localtime(timestamp))


# Conversations database


def init_db():
    """
    Initialize the JSON file database
    """
    if not os.path.exists(CONVERSATION_DB_PATH):
        with open(CONVERSATION_DB_PATH, 'w') as f:
            json.dump({}, f)

    with open(CONVERSATION_DB_PATH) as f:
        conversation_db = json.load(f)

    return conversation_db


def update_conversations():
    """
    Update the side bar conversations from the database
    """
    st.session_state.conversations = get_conversations()


def save_conversation(type: str, question: str, answer: str, id: str = None):
    """
    Save the conversation in the database
    """
    if not id:
        id = str(uuid.uuid4())
    conversation_db = init_db()
    conversation_db[id] = {
        "type": type,
        "question": question,
        "answer": answer,
        "timestamp": time.time(),
    }
    with open(CONVERSATION_DB_PATH, 'w') as f:
        json.dump(conversation_db, f)


def get_conversations():
    """
    Returns the conversations in the database
    """
    conversation_db = init_db()
    conversations = []
    for id, conversation in conversation_db.items():
        conversations.append({
            "id": id,
            "type": conversation["type"],
            "question": conversation["question"],
            "answer": conversation["answer"],
            'timestamp': conversation['timestamp'],
            'date_time': get_date_time(conversation['timestamp']),
        })
    conversations = sorted(conversations, key=lambda x: x['timestamp'],
                           reverse=True)
    return conversations


def get_conversation(id: str):
    """
    Returns the conversation in the database
    """
    conversation_db = init_db()
    if id in conversation_db:
        # assign the date_time field with a human readable date
        conversation_db[id]['date_time'] = \
            get_date_time(conversation_db[id]['timestamp'])
        return conversation_db[id]
    return None


def delete_conversation(id: str):
    """
    Delete a conversation from the database
    """
    conversation_db = init_db()
    if id in conversation_db:
        del conversation_db[id]
        with open(CONVERSATION_DB_PATH, 'w') as f:
            json.dump(conversation_db, f)
        update_conversations()


# OpenAI API


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
    log_debug("get_openai_api_response | " +
              f"{model_params.get('provider', 'N/A')} " +
              f" LLM response: {llm_response}")
    try:
        response['response'] = llm_response.choices[0].message.content
    except Exception as e:
        response['error'] = True
        response['error_message'] = str(e)
    return response


# Rhymes APIs


def aria_query(prompt: str, question: str) -> dict:
    """
    Perform a Aria request
    """
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
    log_debug("aria_query | " +
              f"response: {response}")
    return response


def allegro_query(model_params: dict) -> dict:
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

    query_string = "&".join([f"{key}={value}" for key, value in query.items()])
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
            model_response = requests.post(api_url, headers=headers,
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


def allegro_request_video(question: str):
    """
    Perform a Allegro video generation request
    """
    response = get_default_resultset()

    if REFINE_VIDEO_PROMPT:
        prompt = \
            "I want the refined version of the following prompt for the best" \
            " video generation: {question}" \
            "\n\nGive me just the refined version of the prompt, " \
            "no other text."
        llm_response = aria_query(prompt, question)
        if llm_response['error']:
            return llm_response
        refined_prompt = llm_response['response']

        # Clean the refined prompt
        refined_prompt = refined_prompt.replace("\n", " ")
        refined_prompt = refined_prompt.replace("\r", " ")
        refined_prompt = refined_prompt.replace("Refined Prompt:", "")
        refined_prompt = refined_prompt.strip()
        refined_prompt = refined_prompt.replace('"', '')
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

    response = allegro_query(model_params)

    log_debug("allegro_request_video | GENERATION RESULT | " +
              f"response: {response}")

    if response['error']:
        return response

    if (response["response"].get("message") and
       response["response"]['message'] not in ["Success", '成功']) \
       or not response["response"].get("data"):
        message = response["response"].get("message", "No message and no data")
        response['error'] = True
        response['error_message'] = message

    return response


def allegro_check_video_generation(
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
        response = allegro_query(model_params)
        log_debug(f"allegro_check_video_generation | VERIFICATION {i} | " +
                  f"response: {response}")
        if response['error']:
            return response
        if response["response"]['message'] in ["Success", '成功'] and \
           response["response"].get('data'):
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


def get_suggestions_from_ai(qty: int = 4) -> dict:
    """
    Get suggestions from the AI
    """
    prompt = \
        "I want {question} suggestions for prompts ideas," \
        " half for video generation, half for text generation." \
        "\nGive me just a JSON output with the keys s1, s2, s3, etc, " \
        "and the values for each suggestion."
    llm_response = aria_query(prompt, qty)
    log_debug("get_suggestions_from_ai | " +
              f"response: {llm_response}")
    if llm_response['error']:
        return llm_response
    suggestions = llm_response['response']
    suggestions = suggestions.replace("\n", "")
    suggestions = suggestions.replace("\r", "")
    suggestions = suggestions.replace("Suggestions:", "")
    suggestions = suggestions.strip()
    suggestions = suggestions.replace('```json', '')
    suggestions = suggestions.replace('```', '')
    try:
        suggestions = json.loads(suggestions)
    except Exception as e:
        log_debug(f"get_suggestions_from_ai | ERROR {e}")
        return DEFAULT_SUGGESTIONS
    return suggestions


# UI


def hide_buttons():
    """
    Hide buttons meanwhile the answer is being generated
    """
    st.session_state.show_button = False


def show_buttons():
    """
    Show buttons once the question is answered
    """
    st.session_state.show_button = True


def video_generation(question: str, result_container: st.container):
    # hide_buttons()
    result_container.write("Requesting the videogeneration... "
                           " please hold on...")

    response = allegro_request_video(question)
    if response['error']:
        result_container.write(f"ERROR E-200: {response['error_message']}")
        return

    result_container.write(
        "Please wait while the video is being generated..."
        " It can take 2+ minutes..."
    )

    response = allegro_check_video_generation(response)
    if response['error']:
        result_container.write(f"ERROR E-300: {response['error_message']}")
        return

    if not response.get("video_url"):
        result_container.write("ERROR E-400: Video generation failed."
                               " No video URL")
        return

    video_url = response["video_url"]
    save_conversation(
        type="video",
        question=question,
        answer=video_url,
    )
    result_container.video(video_url)
    # show_buttons()


def text_generation(question: str, result_container: st.container):
    # hide_buttons()
    result_container.write("Generating answer...")

    prompt = "{question}"
    response = aria_query(prompt, question)

    if response['error']:
        result_container.write(f"ERROR E-100: {response['error_message']}")
        return

    save_conversation(
        type="text",
        question=question,
        answer=response['response'],
    )

    result_container.write(response['response'])
    # show_buttons()


def show_conversations():
    """
    Show the conversations in the side bar
    """
    with st.sidebar:
        st.header("Previous answers")
        for conversation in st.session_state.conversations:
            col1, col2 = st.columns(2, gap="small")
            with col1:
                st.button(conversation['question'][:CONVERSATION_LENGTH],
                          key=f"{conversation['id']}",
                          help=conversation['date_time']
                          )
            with col2:
                st.button("X",
                          key=f"del_{conversation['id']}",
                          on_click=delete_conversation,
                          args=(conversation['id'],)
                          )


def show_conversation_content(id: str, container: st.container):
    conversation = get_conversation(id)
    if not conversation:
        container.write("ERROR E-600: Conversation not found")
        return
    with st.expander(f"Conversation with {conversation['type']}"):
        if conversation['type'] == "video":
            container.video(conversation['answer'])
        else:
            container.write(conversation['answer'])


def show_conversation_question(id: str):
    conversation = get_conversation(id)
    st.session_state.question = conversation['question']


def validate_question(question: str):
    """
    Validate the question
    """
    if not question:
        st.write("Please enter a question")
        return False
    st.session_state.question = question
    # update the user input in the conversation
    return True


def main():
    load_dotenv()

    app_name = "VitexBrain"
    maker_name = "The FynBots"

    if "show_button" not in st.session_state:
        st.session_state.show_button = True
    if "question" not in st.session_state:
        st.session_state.question = ""

    # Streamlit app code
    st.set_page_config(
        page_title=app_name,
        page_icon="🍏"
    )

    st.title(app_name)

    # Sidebar
    if "conversations" not in st.session_state:
        update_conversations()
    show_conversations()

    # Main content
    st.write("This App allows you to generate video or answers from a"
             " text prompt")

    st.header("How can we help you?")

    # Suggestes questions
    if "suggestion" not in st.session_state:
        st.session_state.suggestion = get_suggestions_from_ai()

    sug_col1, sug_col2 = st.columns(2)

    with sug_col1:
        sug_col1.button(st.session_state.suggestion["s1"], key="s1")
        sug_col1.button(st.session_state.suggestion["s2"], key="s2")

    with sug_col2:
        sug_col2.button(st.session_state.suggestion["s3"], key="s3")
        sug_col2.button(st.session_state.suggestion["s4"], key="s4")

    # User input
    if st.session_state.get("generate_video") or \
       st.session_state.get("generate_text"):
        update_conversations()
    if st.session_state.get("generate_video") or \
       st.session_state.get("generate_text"):
        st.session_state.suggestion = get_suggestions_from_ai()

    for key in ['s1', 's2', 's3', 's4']:
        if st.session_state.get(key):
            st.session_state.question = st.session_state.suggestion[key]
            break

    for conversation in st.session_state.conversations:
        if st.session_state.get(conversation['id']):
            show_conversation_question(conversation['id'])
            break

    question = st.text_area(
        "Question:",
        st.session_state.question)

    # Buttons

    if st.session_state.show_button:
        col1, col2 = st.columns(2)
        with col1:
            # Generate video button
            col1.button("Generate Video", key="generate_video")

        with col2:
            # Generate text button
            col2.button("Answer Question", key="generate_text")

    result_container = st.empty()

    # Check buttons pushed

    if st.session_state.get("generate_video"):
        if validate_question(question):
            video_generation(st.session_state.question, result_container)

    if st.session_state.get("generate_text"):
        if validate_question(question):
            text_generation(st.session_state.question, result_container)

    for conversation in st.session_state.conversations:
        if st.session_state.get(conversation['id']):
            show_conversation_content(conversation['id'], result_container)
            break

    # Footer
    st.caption(f"© 2024 {maker_name}. All rights reserved.")


if __name__ == "__main__":
    main()
