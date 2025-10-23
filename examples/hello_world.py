"""
Hello World Example - LiteLLM with OpenRouter

This script demonstrates basic usage of LiteLLM with OpenRouter API.
It sends a simple completion request and prints the response.
"""

import os
from dotenv import load_dotenv
import litellm

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenRouter API key")
        print("See .env.example for template")
        return

    # Get model from environment or use default
    model = os.getenv("LITELLM_MODEL", "openrouter/anthropic/claude-haiku-4.5")

    print(f"[INFO] Using model: {model}")
    print("[INFO] Sending request to OpenRouter via LiteLLM...")

    try:
        # Make a simple completion request
        response = litellm.completion(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello World' and explain what you are in one sentence."
                }
            ],
            api_key=api_key,
            timeout=30
        )

        # Extract and print the response
        content = response.choices[0].message.content
        print("\n[SUCCESS] Response received:")
        print("-" * 60)
        print(content)
        print("-" * 60)

        # Print usage statistics
        usage = response.usage
        print(f"\n[INFO] Token usage:")
        print(f"  - Prompt tokens: {usage.prompt_tokens}")
        print(f"  - Completion tokens: {usage.completion_tokens}")
        print(f"  - Total tokens: {usage.total_tokens}")

    except Exception as e:
        print(f"\n[ERROR] Request failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your API key is correct")
        print("2. Verify you have credits on OpenRouter")
        print("3. Check your internet connection")
        return

if __name__ == "__main__":
    main()
