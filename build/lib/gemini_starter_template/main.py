import subprocess
from pathlib import Path
import platform
import toml
from InquirerPy import inquirer

# --------------- User inputs ---------------
project_name = inquirer.text(
    message="Enter your project name:",
    default="agent"
).execute()

dir_type = inquirer.confirm(
    message="Do you want to add a /src directory?",
    default=True
).execute()

uv_command = f"uv init {project_name}"
if dir_type:
    uv_command = f"uv init --package {project_name}"

# --------------- Initialize UV project ---------------
subprocess.run(uv_command, shell=True, check=True)

# Define the project path and venv path
project_path = Path.cwd() / project_name
venv_path = project_path / "venv"

# Create virtual environment inside the project
subprocess.run("uv venv", shell=True, check=True)

# Cross-platform venv activation and install openai-agents
is_windows = platform.system() == "Windows"
if is_windows:
    activate_cmd = f"{venv_path}\\Scripts\\activate"
    install_cmd = f"{activate_cmd} && uv add openai-agents"
    subprocess.run(install_cmd, shell=True, check=True)
else:
    activate_cmd = f"source {venv_path}/bin/activate"
    install_cmd = f"{activate_cmd} && uv add openai-agents"
    subprocess.run(install_cmd, shell=True, executable="/bin/bash", check=True)

# --------------- Gemini agent inputs ---------------
gemini_api_key = inquirer.secret(
    message="Enter Gemini API key:"
).execute()

default_models = ["gemini-2.0-flash", "gemini-2.5-flash", "Custom (type your own)"]
model_choice = inquirer.select(
    message="Choose a Gemini model:",
    choices=default_models
).execute()

if model_choice == "Custom (type your own)":
    model = inquirer.text(message="Enter your Gemini model:").execute()
else:
    model = model_choice

agent_name = inquirer.text(
    message="Enter agent name:",
    default="Helpful Assistant"
).execute()

agent_purpose = inquirer.text(
    message="Enter your agent work:",
    default="You're a helpful assistant, help user with any query"
).execute()

# Write to .env
env_file = project_path / ".env"
env_file.write_text(f"GEMINI_API_KEY={gemini_api_key}\nGEMINI_MODEL={model}\n")

print("Agent Name:", agent_name)
print("Agent Purpose:", agent_purpose)

# --------------- Create agent folder and main.py ---------------
agent_folder = project_path / "agent"
agent_folder.mkdir(exist_ok=True)

main_file = agent_folder / "main.py"
if not main_file.exists():
    main_file.write_text(f"""import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")
    
    print("Agent Name: {agent_name}")
    print("Agent Purpose: {agent_purpose}")
    print("Using Gemini Model: {{model}}")
    # Add your agent logic here

if __name__ == '__main__':
    main()
""")

# --------------- Update pyproject.toml with UV script ---------------
script_name = agent_name.strip().lower().replace(" ", "-")
if not script_name:
    script_name = "helpful-assistant"

pyproject_file = project_path / "pyproject.toml"
if pyproject_file.exists():
    pyproject_data = toml.load(pyproject_file)
else:
    pyproject_data = {}

pyproject_data.setdefault("tool", {}).setdefault("uv", {}).setdefault("scripts", {})
pyproject_data["tool"]["uv"]["scripts"][script_name] = "agent.main:main"

with pyproject_file.open("w") as f:
    toml.dump(pyproject_data, f)

print(f"\n✅ pyproject.toml updated with script '{script_name}'.")
print(f"\n🎉 You can now run your agent with:")
print(f"   uv run {script_name}")
