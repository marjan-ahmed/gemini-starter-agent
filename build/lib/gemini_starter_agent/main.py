import subprocess
from pathlib import Path
import re
import sys

# toml may not be available in some environments, give helpful message
try:
    import toml
except Exception:
    print("ERROR: python 'toml' package is required by the generator. Install it with:")
    print("  pip install toml")
    raise

try:
    from InquirerPy import inquirer
except Exception:
    print("ERROR: InquirerPy is required. Install it with:")
    print("  pip install InquirerPy")
    raise


def sanitize(name: str) -> str:
    s = (name or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "helpful-assistant"


def run_cmd(cmd, cwd=None, shell=False):
    try:
        subprocess.run(cmd, cwd=cwd, shell=shell, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Command failed: {cmd}")
        print(f"Return code: {e.returncode}")
        if cwd:
            print(f"Working dir: {cwd}")
        print("Make sure `uv` is installed and available in PATH (pip install uv).")
        raise


def main():
    # --------------- Collect inputs ---------------
    project_name = inquirer.text(message="Enter your project name:", default="agent").execute()

    gemini_api_key = inquirer.secret(message="Enter Gemini API key:").execute()

    default_models = ["gemini-2.0-flash", "gemini-2.5-flash", "Custom (type your own)"]
    model_choice = inquirer.select(message="Choose a Gemini model:", choices=default_models).execute()
    if model_choice == "Custom (type your own)":
        model = inquirer.text(message="Enter your Gemini model:").execute().strip() or default_models[0]
    else:
        model = model_choice

    agent_name = inquirer.text(message="Enter agent name:", default="Helpful Assistant").execute()
    agent_purpose = inquirer.text(
        message="Enter your agent work:", default="You're a helpful assistant, help user with any query"
    ).execute()

    # --------------- Initialize UV project with src layout ---------------
    uv_command = f"uv init --package {project_name}"
    print(f"\nRunning: {uv_command}")
    run_cmd(uv_command, shell=True)

    project_path = Path.cwd() / project_name
    if not project_path.exists():
        print(f"ERROR: project folder not found at {project_path} after uv init.")
        return

    # --------------- Create venv and install runtime deps ---------------
    print("\nCreating virtual environment with `uv venv`...")
    run_cmd("uv venv", cwd=project_path, shell=True)

    print("\nInstalling runtime packages (openai-agents, python-dotenv) into the project with `uv add`...")
    run_cmd(["uv", "add", "openai-agents", "python-dotenv"], cwd=project_path)
    
    # --------------- Sync environment to actually install the deps ---------------
    print("\nSyncing dependencies with `uv sync`...")
    subprocess.run(["uv", "sync"], cwd=project_path, check=True)


    # --------------- Write .env ---------------
    env_file = project_path / ".env"
    env_file.write_text(f"GEMINI_API_KEY={gemini_api_key} \n GEMINI_MODEL={model}\n", encoding="utf-8")
    print(f"\n✅ .env written to {env_file}")

    print("\nAgent Name:", agent_name)
    print("Agent Purpose:", agent_purpose)

    # --------------- Create the agent package under src/<project_name>/agent ---------------
    src_dir = project_path / "src"
    pkg_root = src_dir / project_name
    pkg_root.mkdir(parents=True, exist_ok=True)

    init_file = pkg_root / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# package initializer\n", encoding="utf-8")

    agent_folder = pkg_root / "agent"
    script_import_target = f"{project_name}.agent:main"

    # --------------- Write agent main.py (if not present) ---------------
    main_file = agent_folder / "main.py"
    if not main_file.exists():
        main_file.write_text(
            f"""import asyncio
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
    name="{agent_name}",
    instructions="{agent_purpose}",
    model=model,
)

async def main() -> None:
    \"\"\"Entry point for the agent CLI.\"\"\" 
    while True:
        prompt = input("Ask a question (or type 'exit' to quit): ")
        if prompt.lower() == "exit":
            break
        result = await Runner.run(agent, prompt, run_config=RunConfig(model))
        print("\\n🤖 Agent:", result.final_output, "\\n")

if __name__ == '__main__':
    asyncio.run(main())
""",
            encoding="utf-8",
        )
        print(f"\n✅ Created {main_file}")

    # --------------- Update pyproject.toml (PEP-621) ---------------
    script_friendly = sanitize(agent_name)
    script_unique = f"{sanitize(project_name)}-{script_friendly}"

    pyproject_file = project_path / "pyproject.toml"
    if pyproject_file.exists():
        pyproject_data = toml.load(pyproject_file)
    else:
        pyproject_data = {}

    project_table = pyproject_data.setdefault("project", {})
    scripts_table = project_table.setdefault("scripts", {})

    scripts_table[script_friendly] = script_import_target
    scripts_table[script_unique] = script_import_target

    with pyproject_file.open("w", encoding="utf-8") as f:
        toml.dump(pyproject_data, f)

    print(f"\n✅ pyproject.toml updated with scripts: '{script_friendly}' and '{script_unique}'.")
    print("\n🎉 Next steps:")
    print(f"  cd {project_path}")
    print(f"  uv run {script_unique}   # recommended (unique, avoids collision)")
    print(f"or\n  uv run {script_friendly}   # friendly name (works when in project folder)")


if __name__ == "__main__":
    main()