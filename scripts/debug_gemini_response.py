#!/usr/bin/env python3
"""Debug script to inspect Gemini API response structure."""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    """Test raw Gemini API response."""
    # Load .env file
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return 1

    print("🔍 Debugging Gemini API Response Structure\n")

    client = genai.Client(api_key=api_key)

    # Simple test prompt
    prompt = "Say 'Hello, World!' and nothing else."

    print(f"📤 Sending prompt: {prompt}")
    print("=" * 60)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1),
        )

        print(f"\n📥 Response object type: {type(response)}")
        print(f"📥 Response attributes: {dir(response)}")
        print("\n" + "=" * 60)

        # Try different ways to access the text
        print("\n🔍 Trying different attribute access methods:")

        if hasattr(response, "text"):
            print(f"  response.text = {response.text}")
            print(f"  response.text type = {type(response.text)}")
        else:
            print("  ❌ response.text does not exist")

        if hasattr(response, "candidates"):
            print(f"\n  response.candidates = {response.candidates}")
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                print(f"  candidate type = {type(candidate)}")
                print(f"  candidate attributes = {dir(candidate)}")
                if hasattr(candidate, "content"):
                    print(f"  candidate.content = {candidate.content}")
                if hasattr(candidate, "text"):
                    print(f"  candidate.text = {candidate.text}")

        # Try to print the raw response
        print(f"\n📄 Raw response: {response}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
