
# Avoid flake8 and pylint errors for long lines
# flake8: noqa
# pylint: disable=line-too-long

CONVERSATION_DB_PATH = "./db/conversations.json"
CONVERSATION_TITLE_LENGTH = 50

VIDEO_GALLERY_COLUMNS = 3

DEFAULT_SUGGESTIONS = {
    "s1": "Step-by-step tutorial to make tea, presented in an animated"
    " format",
    "s2": "Landscape photography of a mountain in the Swiss Alps",
    "s3": "Give me ideas for the summer vacation in Hawaii",
    "s4": "Give me the ReactJs code for a AI Assistant,"
          " using Shadcn/UI",
}

SUGGESTIONS_PROMPT_TEXT = \
    "I want {question} suggestions for prompts ideas," \
    " half for video generation, half for text generation." \
    "\nGive me just a JSON output with the keys s1, s2, s3, etc, " \
    "and the values for each suggestion."
SUGGESTIONS_QTY = 4


REFINE_VIDEO_PROMPT_TEXT = """
Enhance the *USER PROMPT* prompt to make it clear, effective, and suitable for generating a video using a text-to-video AI model.

# Steps

1. Carefully analyze the initial prompt provided.
2. Identify any parts that are unclear or incomplete for generating a video (consider factors like visuals or animation that would be expected for a video format).
3. Add specific guidelines to make the video generation output more vivid and engaging. Ensure context for visual scenes or animations is provided if necessary.
4. Include a clear sequence that’s appropriate for video content, guiding the AI on how to translate ideas into visuals.
5. Ensure the expected output includes direction on storytelling elements, such as scene changes, characters, and any visual effects.

# Output Format

An enhanced version of the prompt that explicitly:
- Adds details for generating video content involving visuals, descriptions, or animations.
- Contains a structured flow to depict a coherent visual representation.
- Defines scene-by-scene instructions if applicable, to assist in generating video content.

# Example

**Initial Prompt (Input)**:  
"Explain why a tomato is a fruit, and then list some related fruits."

**Enhanced Prompt (Output)**:  
"Create a video that explains step-by-step why a tomato is scientifically classified as a fruit. The video should start by depicting a tomato plant, showing its flowers and subsequently its fruit. Add on-screen text explaining its botanical characteristics that belong to fruits, such as having seeds. After emphasizing these characteristics, smoothly transition to displaying other similar fruits, like peppers and cucumbers, with labels for each."

# Notes:

- When enhancing the prompt for video, think visually. Explicitly describe scenes and transitions.
- Include directions on how the video content is structured, such as sequence, timing, and visual focus, to guide the AI effectively.
- Give me just the enhanced version of the prompt, no other text.

*USER PROMPT*
{question}
"""

REFINE_LLM_PROMPT_TEXT = """
Improve the *USER PROMPT* prompt to make it clearer, more effective, and aligned with the task objectives and expectations.

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
- Give me just the enhanced version of the prompt, no other text.

*USER PROMPT*
{question}
"""
