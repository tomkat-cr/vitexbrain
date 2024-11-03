# ViTexBrain

AI Video and Text Generator using Rhymes' Aria and Allegro models.

## Introduction

[VitexBrain](https://vitexbrain.streamlit.app/) is an innovative application that leverages the cutting-edge AI models [Aria](https://rhymes.ai/blog-details/aria-first-open-multimodal-native-moe-model) and [Allegro](https://rhymes.ai/blog-details/allegro-advanced-video-generation-model) by [Rhymes.ai](https://www.rhymes.ai/) to generate high-quality answers and videos from text prompts. This tool is designed to empower developers, researchers, and businesses by providing a seamless and efficient way to create multimodal content. Whether you need to generate videos from scratch or enhance existing content, VitexBrain is your go-to solution for AI-driven creativity.

## Key Features

* Multimodal Native.
* Seamless Integration: Processes text and videos with high-quality results.
* Versatile Outputs: Generates videos from text, and answers questions from text prompts.
* Lightning-Fast Video Processing: Captures and captions 256-frame videos in just 10 seconds.
* Prompts suggestions generates from AI on each form submission and recycle button to refresh them.
* Customizable: Fully available for developers to modify and extend.
* Collaborative: Encourages open-source collaboration and innovation.

## Getting Started

### Prerequisites

* Ptyhon 3.10+
* Make

### Installation

Clone the repository:
```bash
git clone https://github.com/tomkat-cr/vitexbrain.git
```

Navigate to the project directory:

```bash
cd vitexbrain
```

### Create the .env file

Create a `.env` file in the root directory of the project with the following content:

```bash
PYTHON_VERSION=3.10
RHYMES_ARIA_API_KEY=YOUR_RHYMES_ARIA_API_KEY
RHYMES_ALLEGRO_API_KEY=YOUR_RHYMES_ALLEGRO_API_KEY
```

Replace `YOUR_RHYMES_ARIA_API_KEY`, and `YOUR_RHYMES_ALLEGRO_API_KEY` with your actual Rhymes Aria API key, and Rhymes Allegro API key, respectively.

### Run the Application

```bash
# With Make
make run
```

```bash
# Without Make
sh scripts/run_app.sh run
```

## Usage

Go to your favorite Browser and open the URL provided by the application.

* Locally:<BR/>
  [http://localhost:8501](http://localhost:8501)

* Official App:<BR/>
  [https://vitexbrain.streamlit.app/](https://vitexbrain.streamlit.app/)

### Text-to-Video Generation

Enter your text prompt in the provided text box or select one of the suggested prompts.
Click the `Generate Video` button.
Sit back and watch as VitexBrain transforms your text into a high-quality video.
After 2+ minutes, the video will appear in the video container.
All videos are available in the side menu and stored in a JSON file localted in the `db` folder.

### Text-to-Text Generation

Enter your text prompt in the provided text box or select one of the suggested prompts.
Click the `Answer Question` button.
The answer will appear in the text container.
All questions and answers are available in the side menu and stored in a JSON file localted in the `db` folder.

## Contributors

Carlos J. Ramirez <tomkat_cr@yahoo.com>
Tajmir khan <tajmirkhan515@gmail.com>

Please feel free to suggest improvements, report bugs, or make a contribution to the code.

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

* [Rhymes.ai](https://www.rhymes.ai/) for developing the powerful [Aria](https://rhymes.ai/blog-details/aria-first-open-multimodal-native-moe-model) and [Allegro](https://rhymes.ai/blog-details/allegro-advanced-video-generation-model) models.
* [Streamlit](https://streamlit.io/) for providing a user-friendly interface for interacting with the application.
* Open-source community for inspiring and supporting collaborative innovation.
* Users and contributors for their feedback and support.
