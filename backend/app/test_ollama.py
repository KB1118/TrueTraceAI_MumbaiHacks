import asyncio
import httpx
import json

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "gpt-oss:20b-cloud"  # Change this to the model you have installed (e.g., mistral, llama2, qwen)

async def test_endpoint(client, name, url, payload=None, method="GET"):
    print(f"\n--- Testing {name} ---")
    print(f"URL: {url}")
    try:
        if method == "GET":
            response = await client.get(url)
        else:
            response = await client.post(url, json=payload, timeout=30.0)
            
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                # Print a snippet of the response
                print(f"Success! Response snippet: {str(data)[:100]}...")
                return True
            except json.JSONDecodeError:
                print(f"Success (No JSON)! Response text: {response.text}")
                return True
        else:
            print(f"Failed. Response: {response.text}")
            return False
            
    except httpx.ConnectError:
        print("Connection Failed: Is Ollama running?")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Test Base Connectivity
        print(f"Checking if Ollama is running at {OLLAMA_BASE_URL}...")
        is_running = await test_endpoint(client, "Root URL", OLLAMA_BASE_URL)
        
        if not is_running:
            print("\nCRITICAL: Could not connect to Ollama. Make sure the app is running (e.g., 'ollama serve').")
            return

        # 2. List Models (This confirms the API is working)
        print("\nChecking available models...")
        await test_endpoint(client, "List Models (/api/tags)", f"{OLLAMA_BASE_URL}/api/tags")

        # Payload for generation tests
        chat_payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": "Say hello!"}],
            "stream": False
        }

        # 3. Test Native Ollama Endpoint (/api/chat)
        # This is the standard endpoint for Ollama.
        print(f"\nTesting Native Chat ({OLLAMA_BASE_URL}/api/chat)...")
        native_success = await test_endpoint(
            client, 
            "Native Chat", 
            f"{OLLAMA_BASE_URL}/api/chat", 
            chat_payload, 
            method="POST"
        )

        # 4. Test OpenAI-Compatible Endpoint (/v1/chat/completions)
        # This is the one currently failing in your logs.
        print(f"\nTesting OpenAI-Compatible Chat ({OLLAMA_BASE_URL}/v1/chat/completions)...")
        openai_success = await test_endpoint(
            client, 
            "OpenAI Compat Chat", 
            f"{OLLAMA_BASE_URL}/v1/chat/completions", 
            chat_payload, 
            method="POST"
        )

        print("\n" + "="*30)
        print("DIAGNOSIS REPORT")
        print("="*30)
        if native_success and not openai_success:
            print("❌ Your Ollama supports native '/api/chat' but fails on '/v1/chat/completions'.")
            print("   FIX: In 'ollama_client.py', ensure you are NOT forcing OpenAI mode.")
            print("   Check your .env file: Ensure OLLAMA_API_KEY is empty or not set.")
        elif not native_success and not openai_success:
            print("❌ Both endpoints failed. Check if the model name is correct.")
            print(f"   Target Model: {MODEL_NAME}")
        elif openai_success:
            print("✅ OpenAI endpoint is working. The issue might be the URL in your config.")

if __name__ == "__main__":
    asyncio.run(main())