from setuptools import setup, find_packages

setup(
    name="gemini-starter-agent",  
    version="0.2.0",
    description="A CLI tool to bootstrap Gemini agents with OpenAI Agent SDK using UV.",
    author="Marjan Ahmed",
    author_email="marjanahmed.dev@gmail.com",
    packages=find_packages(exclude=["tests*", "examples*"]),  # avoid shipping test/example files
    install_requires=[
        "python-dotenv",  # only what your package actually needs
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "helpful-assistant=agent.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # or your license
        "Operating System :: OS Independent",
    ],
)
