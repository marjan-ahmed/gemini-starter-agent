import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")
    
    print("Agent Name: My assistant")
    print("Agent Purpose: You're a helpful assistant, help user with any query")
    print("Using Gemini Model: {model}")
    # Add your agent logic here

if __name__ == '__main__':
    main()
