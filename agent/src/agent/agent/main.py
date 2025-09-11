import asyncio
import os
from dotenv import load_dotenv
# the openai-agents runtime packages are installed by `uv add`
from Agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel, set_tracing_disabled
from OpenAI import AsyncOpenAI

# Load environment variables
load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Disable tracing for cleaner output
set_tracing_disabled(True)

# Setup OpenAI async client + model
client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(GEMINI_MODEL, client)

# Define a simple agent
agent: Agent = Agent(
    name="Helpful Assistant",
    instructions="You're a helpful assistant, help user with any query",
    model=model,
)

async def main() -> None:
    """Entry point for the agent CLI.""" 
    while True:
        prompt = input("Ask a question (or type 'exit' to quit): ")
        if prompt.lower() == "exit":
            break
        result = await Runner.run(agent, prompt, run_config=RunConfig(model))
        print("\n🤖 Agent:", result.final_output, "\n")

if __name__ == '__main__':
    asyncio.run(main())
