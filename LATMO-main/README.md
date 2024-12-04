# LATMO Multi-Agent AI Assistant

## Overview
LATMO is a powerful multi-agent AI assistant built with Streamlit, LangChain, and various AI models. It provides an interactive web interface to interact with different AI agents and tools.

## Features
- Top Level Agent
- Coder Agent
- Wikipedia Agent
- Gmail Agent
- Google Calendar Agent
- Local RAG (Retrieval-Augmented Generation) Agent
- Notepad Agent

## Prerequisites
- Python 3.8+
- pip (Python package manager)

## Setup Instructions

1. Clone the repository
```bash
git clone https://github.com/your-repo/LATMO.git
cd LATMO
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up Google and other API credentials
- Obtain necessary API keys for Google services
- Place credentials in appropriate configuration files

5. Run the Streamlit App
```bash
streamlit run main/app.py
```

## Configuration
- Modify `main/app.py` to customize agent behaviors
- Update `requirements.txt` for dependency management

## Troubleshooting
- Ensure all API credentials are correctly configured
- Check Python and package versions
- Verify network connectivity for external API calls

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
