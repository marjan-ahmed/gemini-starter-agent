import subprocess
from pathlib import Path
import re

base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

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
    project_name = inquirer.text(message="Enter your project name:").execute()

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

    # --------------- Write .env ---------------
    env_file = project_path / ".env"
    env_file.write_text(f"GEMINI_API_KEY={gemini_api_key}\nGEMINI_MODEL={model}\nBASE_URL={base_url}", encoding="utf-8")

    # --------------- Convert project name to valid Python module name ---------------
    # Replace hyphens with underscores for the actual Python module
    module_name = project_name.replace("-", "_")
    
    # Create the package root at src/<module_name>
    src_dir = project_path / "src"
    pkg_root = src_dir / module_name
    pkg_root.mkdir(parents=True, exist_ok=True)

    init_file = pkg_root / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# package initializer\n", encoding="utf-8")

    # We'll write main.py directly under src/<module_name>/main.py
    script_import_target = f"{module_name}:main"

    main_file = pkg_root / "main.py"
    if not main_file.exists():
        main_file.write_text(
            f"""import asyncio
import os
from dotenv import load_dotenv
# the openai-agents runtime packages are installed by `uv add`
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
""",
            encoding="utf-8",
        )

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

    # Use the valid module name (with underscores) for the import target
    script_import_target = f"{module_name}.main:start"

    scripts_table[script_friendly] = script_import_target
    scripts_table[script_unique] = script_import_target

    with pyproject_file.open("w", encoding="utf-8") as f:
        toml.dump(pyproject_data, f)

    print("\n🎉 Next steps:")
    print(f"    cd {project_name}")
    print(f"    uv run {script_friendly}\n")


if __name__ == "__main__":
    main()