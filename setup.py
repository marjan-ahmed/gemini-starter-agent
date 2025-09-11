from setuptools import setup, find_packages

setup(
    name="gemini-starter-agent",
    version="0.6.0",
    description="A CLI tool to bootstrap Gemini agents with OpenAI Agent SDK using UV.",
    author="Marjan Ahmed",
    author_email="marjanahmed.dev@gmail.com",
    packages=find_packages(exclude=["tests*", "examples*"]),
    install_requires=[
        "python-dotenv",
        "InquirerPy",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "gemini-starter-agent=gemini_starter_agent.main:main",  # <-- FIXED
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)