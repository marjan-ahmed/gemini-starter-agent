Gemini Starter Agent - Simplifying Gemini Chat Completions in the OpenAI Agents SDK
======================================================================================

[https://img.shields.io/badge/python-3.13+-blue](https://img.shields.io/badge/python-3.13+-blue)[https://img.shields.io/badge/License-MIT-yellow.svg](https://img.shields.io/badge/License-MIT-yellow.svg)

Gemini Starter Agent is a Python CLI tool to quickly bootstrap AI agents using the Gemini API and OpenAI Agent SDK. It leverages [UV](https://uv-pypi.org/) for project scaffolding, virtual environment management, and dependency handling.

Features
--------

*   Quick scaffolding of a Gemini AI agent project.
    
*   Automatic creation of virtual environments.
    
*   Easy dependency installation (openai-agents, python-dotenv).
    
*   Generates a ready-to-run main.py for your agent.
    
*   Friendly CLI prompts for agent name, purpose, and API key.
    
*   PEP-621 compliant pyproject.toml scripts for easy CLI execution.
    
*   Cross-platform support.
    

Installation
------------
Install the package via pip:

```bash
pip install gemini-starter-agent
```

Usage
-----

Run the CLI to generate a new Gemini agent:

```bash
`pip install gemini-starter-agent   `

```

You will be prompted for:

*   Project name (default: agent)
    
*   Gemini API key
    
*   Gemini model (choose from default or enter your own)
    
*   Agent name (default: Helpful Assistant)
    
*   Agent purpose/instructions
    

After completion, your project structure will look like:

```Plain 
/your-project-name/
├── src/
│   └── your_project_name/
│       ├── __init__.py
│       └── main.py
├── .env
├── pyproject.toml
└── uv.lock
```

Example main.py
---------------

Here is how the generated main.py will look:

```python
import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Disable tracing for cleaner output
set_tracing_disabled(True)

client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(GEMINI_MODEL, client)

agent: Agent = Agent(
    name="{agent_name}",
    instructions="{agent_purpose}",
    model=model,
)

async def main() -> None:
    prompt = "What is Agentic AI? The output format should be in haiku" # enter a prompt here
    result = await Runner.run(agent, prompt, run_config=RunConfig(model))
    print(result.final_output)

def start():
    asyncio.run(main())
```

Running Your Agent
------------------

Change into the project folder:


Run the agent using UV scripts:

```sh
cd [project_name]
uv run helpful-assistant               

```

Environment Variables
---------------------

The .env file is automatically generated and contains:

```sh
GEMINI_API_KEY=your_api_key_here  
GEMINI_MODEL=your_model_here  
BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`
```

Contributing
------------
*   Submit bug reports or feature requests via GitHub Issues.
    
*   Fork the repository and create pull requests for improvements.
    
*   Ensure code style consistency and add documentation for new features.
    

License
-------

This project is licensed under the **MIT License**. See the [LICENSE](https://github.com/marjan-ahmed/gemini-starter-agent/blob/main/LICENSE.md/) file for details.

Author
------

**Marjan Ahmed**

*   Email: [marjanahmed.dev@gmail.com](https://mailto:marjanahmed.dev@gmail.com/)    
*   GitHub: [https://github.com/marjan-ahmed](https://github.com/marjan-ahmed)
*   Portfolio: [https://marjanahmed.vercel.app](https://marjanahmed.vercel.app)