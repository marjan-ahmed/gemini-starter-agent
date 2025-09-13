from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="gemini-starter-agent",
    version="0.1.1",
    description="A CLI tool to bootstrap Gemini agents with OpenAI Agent SDK using UV.",
    author="Marjan Ahmed",
    author_email="marjanahmed.dev@gmail.com",
    packages=find_packages(exclude=["tests*", "examples*"]),
    install_requires=[
        "python-dotenv",
        "InquirerPy",
    ],
    python_requires=">=3.13",
    entry_points={
        "console_scripts": [
            "gemini-starter-agent=gemini_starter_agent.main:main",  
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)