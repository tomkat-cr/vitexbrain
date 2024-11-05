"""
VitexBrain App
"""
import os

from dotenv import load_dotenv
import streamlit as st

from src.codegen_utilities import (
    get_default_resultset,
)
from src.codegen_streamlit_lib import CodegenStreamlitLib

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


cgsl = CodegenStreamlitLib({
    "CONVERSATION_DB_PATH": CONVERSATION_DB_PATH,
    "CONVERSATION_TITLE_LENGTH": CONVERSATION_TITLE_LENGTH,
    "VIDEO_GALLERY_COLUMNS": VIDEO_GALLERY_COLUMNS,
    "DEFAULT_SUGGESTIONS": DEFAULT_SUGGESTIONS,
    "SUGGESTIONS_PROMPT_TEXT": SUGGESTIONS_PROMPT_TEXT,
    "SUGGESTIONS_QTY": SUGGESTIONS_QTY,
    "REFINE_VIDEO_PROMPT_TEXT": REFINE_VIDEO_PROMPT_TEXT,
    "REFINE_LLM_PROMPT_TEXT": REFINE_LLM_PROMPT_TEXT,
})


# VitexBrain specific


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


def add_footer():
    """
    Add the footer to the page
    """
    st.caption(f"© 2024 {st.session_state.maker_name}. All rights reserved.")


def page_1():
    # Get suggested questions initial value
    with st.spinner("Loading App..."):
        if "suggestion" not in st.session_state:
            cgsl.recycle_suggestions()

    # Main content

    tit_col1, tit_col2 = st.columns(2, gap="small",
                                    vertical_alignment="bottom")
    with tit_col1:
        st.title(f"{st.session_state.app_name} {st.session_state.app_icon}")
    with tit_col2:
        st.button("Video Gallery",
                  on_click=cgsl.set_query_param,
                  args=("page", "gallery"))

    # Suggestions
    suggestion_container = st.empty()
    cgsl.show_suggestion_components(suggestion_container)

    # Show the siderbar selected conversarion's question and answer in the
    # main section
    # (must be done before the user input)
    for conversation in st.session_state.conversations:
        if st.session_state.get(conversation['id']):
            cgsl.show_conversation_question(conversation['id'])
            break

    # User input
    question = st.text_area(
        "Question / Prompt:",
        st.session_state.question)

    # "generate_video" and "generate_text" Buttons
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
                      on_change=cgsl.prompt_enhancement)

    # Results containers
    additional_result_container = st.empty()
    result_container = st.empty()

    # Show the selected conversation's question and answer in the
    # main section
    if "new_id" in st.session_state:
        # log_debug("main | Showing conversation with " +
        #           f"st.session_state.new_id: {st.session_state.new_id}")
        cgsl.show_conversation_question(st.session_state.new_id)
        cgsl.show_conversation_content(
            st.session_state.new_id,
            cgsl.result_container,
            cgsl.additional_result_container)
        st.session_state.new_id = None

    # Sidebar
    with st.sidebar:
        st.sidebar.write(
            f"**{st.session_state.app_name}** allows you to generate "
            "video or answers from a text prompt")

        st.button("Go to Video Gallery Page",
                  on_click=cgsl.set_query_param,
                  args=("page", "gallery"))

        cgsl.data_management_components()
        data_management_container = st.empty()

        # Show the conversations in the side bar
        cgsl.show_conversations()

    # Check buttons pushed

    # Process the generate_video button pushed
    if st.session_state.get("generate_video"):
        cgsl.video_generation(result_container, question)

    # Process the generate_text button pushed
    if st.session_state.get("generate_text"):
        cgsl.text_generation(result_container, question)

    # Show the selected conversation's question and answer in the
    # main section
    for conversation in st.session_state.conversations:
        if st.session_state.get(conversation['id']):
            cgsl.show_conversation_content(
                conversation['id'], result_container,
                additional_result_container)
            break

    # Perform data management operations
    if st.session_state.get("import_data"):
        cgsl.import_data(data_management_container)

    if st.session_state.get("export_data"):
        cgsl.export_data(data_management_container)

    if "dm_results" in st.session_state and st.session_state.dm_results:
        cgsl.success_message(
            "Operation result:\n\n" +
            f"{cgsl.format_results(st.session_state.dm_results)}",
            container=data_management_container)
        st.session_state.dm_results = None

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
            on_click=cgsl.set_query_param,
            args=("page", "home"),
        )

    # Define video URLs
    video_urls = get_video_urls()

    # log_debug("page_2 | video_urls: " + f"{video_urls}")

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

    if "question" not in st.session_state:
        st.session_state.question = ""
    if "prompt_enhancement_flag" not in st.session_state:
        st.session_state.prompt_enhancement_flag = False
    if "conversations" not in st.session_state:
        cgsl.update_conversations()

    # Streamlit app code
    st.set_page_config(
        page_title=st.session_state.app_name,
        page_icon=st.session_state.app_icon,
        layout="wide",
        initial_sidebar_state="auto",
    )

    # Query params to handle navigation
    page = st.query_params.get("page", "home")
    # log_debug("main | page: " + f"{page}")

    # Page navigation logic
    if page == "home":
        page_1()
    elif page == "gallery":
        page_2()


if __name__ == "__main__":
    main()
