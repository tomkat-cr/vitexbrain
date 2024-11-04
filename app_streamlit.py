
import os
import time
import json

from dotenv import load_dotenv
import uuid
import streamlit as st

from src.codegen_utilities import (
    log_debug,
    get_date_time,
    get_default_resultset,
)
from src.codegen_db import CodegenDatabase
from src.codegen_ai_utilities import TextToVideoProvider, LlmProvider

from app_streamlit_contants import (
    CONVERSATION_DB_PATH,
    CONVERSATION_TITLE_LENGTH,
    VIDEO_GALLERY_COLUMNS,
    DEFAULT_SUGGESTIONS,
    SUGGESTIONS_PROMPT_TEXT,
    SUGGESTIONS_QTY,
    REFINE_VIDEO_PROMPT_TEXT,
    REFINE_LLM_PROMPT_TEXT,
)


# General utilities and functions


def set_new_id(id: str = None):
    """
    Set the new id global variable
    """
    if "new_id" not in st.session_state:
        st.session_state.new_id = None
    st.session_state.new_id = id


def get_new_id():
    """
    Get the new id global variable
    """
    if "new_id" in st.session_state:
        return st.session_state.new_id
    else:
        return "No new_id"


def prompt_enhancement():
    """
    Prompt enhancement checkbox callback
    """
    st.session_state.prompt_enhancement_flag = False
    if "prompt_enhancement" in st.session_state:
        if st.session_state.prompt_enhancement:
            st.session_state.prompt_enhancement_flag = True


# Conversations database


def init_db():
    """
    Initialize the JSON file database
    """
    db_type = os.getenv('DB_TYPE')
    db = None
    if db_type == 'json':
        db = CodegenDatabase("json", {
            "JSON_DB_PATH": os.getenv('JSON_DB_PATH', CONVERSATION_DB_PATH),
        })
    if db_type == 'mongodb':
        db = CodegenDatabase("mongodb", {
            "MONGODB_URI": os.getenv('MONGODB_URI'),
            "MONGODB_DB_NAME": os.getenv('MONGODB_DB_NAME'),
            "MONGODB_COLLECTION_NAME": os.getenv('MONGODB_COLLECTION_NAME'),
        })
    if not db:
        raise ValueError(f"Invalid DB_TYPE: {db_type}")
    return db


def update_conversations():
    """
    Update the side bar conversations from the database
    """
    st.session_state.conversations = get_conversations()


def get_new_item_id():
    """
    Get the new unique item id
    """
    return str(uuid.uuid4())


def save_conversation(type: str, question: str, answer: str,
                      refined_prompt: str = None,
                      ttv_response: dict = None, id: str = None):
    """
    Save the conversation in the database
    """
    if not id:
        id = get_new_item_id()
    db = init_db()
    item = {
        "type": type,
        "question": question,
        "answer": answer,
        "ttv_response": ttv_response,
        "refined_prompt": refined_prompt,
        "timestamp": time.time(),
    }
    db.save_item(item, id)
    update_conversations()
    recycle_suggestions()
    set_new_id(id)
    return id


def get_conversations():
    """
    Returns the conversations in the database
    """
    db = init_db()
    conversations = db.get_list("timestamp", "desc")
    # Add the date_time field to each conversation
    for conversation in conversations:
        conversation['date_time'] = get_date_time(conversation['timestamp'])
    return conversations


def get_conversation(id: str):
    """
    Returns the conversation in the database
    """
    db = init_db()
    conversation = db.get_item(id)
    if conversation:
        # Add the date_time field to the conversation
        conversation['date_time'] = get_date_time(conversation['timestamp'])
        return conversation
    return None


def delete_conversation(id: str):
    """
    Delete a conversation from the database
    """
    db = init_db()
    db.delete_item(id)
    update_conversations()


def get_suggestions_from_ai(prompt: str, qty: int = 4) -> dict:
    """
    Get suggestions from the AI
    """
    llm_model = LlmProvider({
        "provider": os.environ.get("LLM_PROVIDER"),
    })
    llm_response = llm_model.query(prompt, qty)
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


def recycle_suggestions():
    """
    Recycle the suggestions from the AI
    """
    st.session_state.suggestion = get_suggestions_from_ai(
        SUGGESTIONS_PROMPT_TEXT, SUGGESTIONS_QTY)


def video_generation(result_container: st.container, question: str = None,
                     previous_response: dict = None):
    # hide_buttons()
    ttv_model = TextToVideoProvider({
        "provider": os.environ.get("TEXT_TO_VIDEO_PROVIDER"),
    })
    if previous_response:
        response = previous_response.copy()
        video_id = response['id']
    else:
        video_id = get_new_item_id()
        if not question:
            question = st.session_state.question
        if not validate_question(question):
            return
        with st.spinner("Requesting the video generation..."):
            # Requesting the video generation
            response = ttv_model.request(
                question,
                (REFINE_VIDEO_PROMPT_TEXT if
                 st.session_state.prompt_enhancement_flag else None)
            )
            if response['error']:
                result_container.write(
                    f"ERROR E-200: {response['error_message']}")
                return

    with st.spinner("Procesing video generation. It can last 2+ minutes..."):
        #  Checking the video generation status
        video_url = None
        ttv_response = response.copy()
        ttv_response['id'] = video_id

        # Save a preliminar conversation with the video generation request
        # follow-up data in the ttv_response attribute
        save_conversation(
            type="video",
            question=question,
            refined_prompt=ttv_response['refined_prompt'],
            answer=video_url,
            ttv_response=ttv_response,
            id=video_id,
        )

        response = ttv_model.generation_check(ttv_response)
        if response['error']:
            result_container.write(
                f"ERROR E-300: {response['error_message']}")
            return

        if not response.get("video_url"):
            result_container.write("ERROR E-400: Video generation failed."
                                   " No video URL. Try again later by clicking"
                                   " the corresponding previous answer.")
        else:
            video_url = response["video_url"]

        # Save the conversation with the video generation result
        save_conversation(
            type="video",
            question=question,
            refined_prompt=ttv_response['refined_prompt'],
            answer=video_url,
            ttv_response=ttv_response,
            id=video_id,
        )
        # result_container.video(video_url)
        # show_buttons()
        st.rerun()


def text_generation(result_container: st.container, question: str = None):
    # hide_buttons()
    if not question:
        question = st.session_state.question
    if not validate_question(question):
        return

    with st.spinner("Procesing text generation..."):
        # Generating answer
        llm_model = LlmProvider({
            "provider": os.environ.get("LLM_PROVIDER"),
        })
        prompt = "{question}"
        response = llm_model.query(
            prompt, question,
            (REFINE_LLM_PROMPT_TEXT if
             st.session_state.prompt_enhancement_flag else None)
        )
        if response['error']:
            result_container.write(f"ERROR E-100: {response['error_message']}")
            return
        save_conversation(
            type="text",
            question=question,
            refined_prompt=response['refined_prompt'],
            answer=response['response'],
        )
        # result_container.write(response['response'])
        # show_buttons()
        st.rerun()


def get_video_urls():
    """
    Returns a list of video URLs
    """
    response = get_default_resultset()
    response['urls'] = []
    for conversation in st.session_state.conversations:
        if conversation['type'] == "video":
            if conversation.get('answer'):
                response['urls'].append(conversation['answer'])
    return response


def show_conversations():
    """
    Show the conversations in the side bar
    """
    st.header("Previous answers")
    for conversation in st.session_state.conversations:
        col1, col2 = st.columns(2, gap="small")
        with col1:
            st.button(
                conversation['question'][:CONVERSATION_TITLE_LENGTH],
                key=f"{conversation['id']}",
                help=f"{conversation['type'].capitalize()} generated on " +
                     f"{conversation['date_time']}")
        with col2:
            st.button(
                "x",
                key=f"del_{conversation['id']}",
                on_click=delete_conversation,
                args=(conversation['id'],))


def show_conversation_content(
    id: str, container: st.container,
    additional_container: st.container
):
    """
    Show the conversation content
    """
    if not id:
        return
    conversation = get_conversation(id)
    if not conversation:
        container.write("ERROR E-600: Conversation not found")
        return
    if conversation.get('refined_prompt'):
        log_debug(
            "SHOW_CONVERSATION_CONTENT | " +
            f"\n | conversation['question']: {conversation['question']}"
            "\n | conversation['refined_prompt']: "
            f"{conversation['refined_prompt']}"
        )
        with additional_container.expander(
             f"Enhanced Prompt for {conversation['type'].capitalize()}"):
            st.write(conversation['refined_prompt'])
    if conversation['type'] == "video":
        if conversation.get('answer'):
            container.video(conversation['answer'])
        else:
            video_generation(
                container, conversation['question'],
                conversation['ttv_response'])
    else:
        container.write(conversation['answer'])


def show_conversation_question(id: str):
    if not id:
        return
    conversation = get_conversation(id)
    st.session_state.question = conversation['question']


def validate_question(question: str):
    """
    Validate the question
    """
    if not question:
        st.write("Please enter a question / prompt")
        return False
    # Update the user input in the conversation
    st.session_state.question = question
    return True


def add_footer():
    """
    Add the footer to the page
    """
    st.caption(f"© 2024 {st.session_state.maker_name}. All rights reserved.")


def set_query_param(name, value):
    """
    Set a URL query parameter
    """
    st.query_params[name] = value


def page_1():
    # Get suggested questions initial value
    with st.spinner("Loading App..."):
        if "suggestion" not in st.session_state:
            recycle_suggestions()

    # Main content

    tit_col1, tit_col2 = st.columns(2, gap="small",
                                    vertical_alignment="bottom")
    with tit_col1:
        st.title(f"{st.session_state.app_name} {st.session_state.app_icon}")
    with tit_col2:
        st.button("Video Gallery",
                  on_click=set_query_param,
                  args=("page", "gallery"))

    # Suggestions
    if st.session_state.get("recycle_suggestions"):
        with st.spinner("Recycling suggestions..."):
            recycle_suggestions()

    # Show the 4 suggestions in the main section
    sug_col1, sug_col2, sug_col3 = st.columns(
        3, gap="small",
    )
    with sug_col1:
        sug_col1.button(st.session_state.suggestion["s1"], key="s1")
        sug_col1.button(st.session_state.suggestion["s2"], key="s2")

    with sug_col2:
        sug_col2.button(st.session_state.suggestion["s3"], key="s3")
        sug_col2.button(st.session_state.suggestion["s4"], key="s4")

    with sug_col3:
        sug_col3.button(
            ":recycle:",
            key="recycle_suggestions",
            help="Recycle suggestions buttons",
        )

    # Process the suggestion button pushed (must be done before the user input)
    for key in ['s1', 's2', 's3', 's4']:
        if st.session_state.get(key):
            st.session_state.question = st.session_state.suggestion[key]
            break

    # Show the siderbar selected conversarion's question and answer in the
    # main section
    # (must be done before the user input)
    for conversation in st.session_state.conversations:
        if st.session_state.get(conversation['id']):
            show_conversation_question(conversation['id'])
            break

    # User input
    question = st.text_area(
        "Question / Prompt:",
        st.session_state.question)

    # "generate_video" and "generate_text" Buttons
    if st.session_state.show_button:
        col1, col2, col3 = st.columns(3)
        with col1:
            # Generate video button
            col1.button("Generate Video", key="generate_video")
        with col2:
            # Generate text button
            col2.button("Answer Question", key="generate_text")
        with col3:
            # Enhance prompt checkbox
            col3.checkbox("Enhance prompt", key="prompt_enhancement",
                          on_change=prompt_enhancement)

    additional_result_container = st.empty()
    result_container = st.empty()

    if "new_id" in st.session_state:
        log_debug("main | Showing conversation with " +
                  f"st.session_state.new_id: {st.session_state.new_id}")
        show_conversation_question(st.session_state.new_id)
        show_conversation_content(st.session_state.new_id, result_container,
                                  additional_result_container)
        st.session_state.new_id = None

    # Sidebar
    with st.sidebar:
        st.sidebar.write(
            f"**{st.session_state.app_name}** allows you to generate "
            "video or answers from a text prompt")

        st.button("Go to Video Gallery Page",
                  on_click=set_query_param,
                  args=("page", "gallery"))

        # Show the conversations in the side bar
        show_conversations()

    # Check buttons pushed

    # Process the generate_video button pushed
    if st.session_state.get("generate_video"):
        video_generation(result_container, question)

    # Process the generate_text button pushed
    if st.session_state.get("generate_text"):
        text_generation(result_container, question)

    # Show the selected conversation's question and answer in the
    # main section
    for conversation in st.session_state.conversations:
        if st.session_state.get(conversation['id']):
            show_conversation_content(conversation['id'], result_container,
                                      additional_result_container)
            break

    # Footer
    add_footer()


# Page 2: Gallery of videos with 3 columns
def page_2():

    head_col1, head_col2 = st.columns(
        2, gap="small",
        vertical_alignment="bottom")
    with head_col1:
        head_col1.title(
            f"{st.session_state.app_name} {st.session_state.app_icon}"
            " Video Gallery")
        head_col2.button(
            "Generate Content",
            key="go_to_text_generation",
            help="Generate more videos from text prompts",
            on_click=set_query_param,
            args=("page", "home"),
        )

    # Define video URLs
    video_urls = get_video_urls()

    log_debug("page_2 | video_urls: " + f"{video_urls}")

    if not video_urls['urls']:
        st.write("No videos found. Try again later.")
        return

    # Display videos in a 3-column layout
    cols = st.columns(VIDEO_GALLERY_COLUMNS)
    for i, video_url in enumerate(video_urls['urls']):
        with cols[i % VIDEO_GALLERY_COLUMNS]:
            st.video(video_url)

    # Footer
    add_footer()


# Main function to render pages
def main():
    load_dotenv()

    st.session_state.app_name = os.environ.get("APP_MAME", "VitexBrain")
    st.session_state.maker_name = os.environ.get("MAKER_MAME", "The FynBots")
    st.session_state.app_icon = os.environ.get("APP_ICON", ":brain:")

    if "show_button" not in st.session_state:
        st.session_state.show_button = True
    if "question" not in st.session_state:
        st.session_state.question = ""
    if "prompt_enhancement_flag" not in st.session_state:
        st.session_state.prompt_enhancement_flag = False
    if "conversations" not in st.session_state:
        update_conversations()

    # Streamlit app code
    st.set_page_config(
        page_title=st.session_state.app_name,
        page_icon=st.session_state.app_icon,
        layout="wide",
        initial_sidebar_state="auto",
    )

    # Query params to handle navigation
    page = st.query_params.get("page", "home")
    log_debug("main | page: " + f"{page}")

    # Page navigation logic
    if page == "home":
        page_1()
    elif page == "gallery":
        page_2()


if __name__ == "__main__":
    main()
