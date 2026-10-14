
import os
from openai import OpenAI

# Connect to Ollama's cloud API
client = OpenAI(
    base_url="https://ollama.com/v1",
    api_key=os.environ["OLLAMA_API_KEY"],
)

MODEL = "gemma4:31b"

# Define the assistant's role
system_prompt = """
You are my personal AI assistant.

Your responsibilities:
- Answer questions clearly.
- Help me solve problems.
- Help me plan and organize tasks.
- Ask questions when you need more information.
- Be honest when you don't know something.
- Never claim to have performed an action
  unless you actually performed it.

Be helpful, practical, and concise.
"""

# Store the conversation in memory while the program runs
messages = [
    {"role": "system", "content": system_prompt}
]

print("Personal AI Assistant is ready!")
print("Type 'exit' to stop.\n")

while True:
    try:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("Assistant: Goodbye!")
            break

        if not user_input:
            continue

        # Add your message to the conversation
        messages.append({
            "role": "user",
            "content": user_input
        })

        # Ask the AI to respond
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        answer = response.choices[0].message.content

        # Display the answer
        print(f"\nAssistant: {answer}\n")

        # Save the answer in the conversation history
        messages.append({
            "role": "assistant",
            "content": answer
        })

    except KeyboardInterrupt:
        print("\nAssistant: Goodbye!")
        break

    except Exception as error:
        print(f"\nAn error occurred: {error}\n")
