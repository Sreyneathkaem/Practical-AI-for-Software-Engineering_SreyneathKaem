"""
AskBot — Session 1 Lab starter
Practical AI for Software Engineering · Week 1

Work through the PARTs in order. Each has TODOs. Run the file after every part:
    python askbot.py

You only need to edit the sections marked TODO. Helper wiring is done for you.
"""

import os
import sys
import time
import argparse
from dotenv import load_dotenv
from openai import OpenAI

# --- provider wiring (done for you) ----------------------------------------
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("LLM_API_KEY"),
    base_url=os.environ.get("LLM_BASE_URL"),
)
MODEL = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")

# Token estimation (rough approximation: ~4 chars per token)
CHARS_PER_TOKEN = 4


# ===========================================================================
# PART 1 — Your first completion
#   Goal: send one prompt, print the reply.
# ===========================================================================
def ask_once(prompt: str) -> str:
    """Send a single message and get a response."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


# ===========================================================================
# PART 2 — Interactive REPL with memory
#   Goal: a loop that keeps the conversation so the bot remembers context.
# ===========================================================================
def chat_loop(system_prompt: str, temperature: float):
    """
    Interactive chat loop with conversation memory.
    
    Args:
        system_prompt: The system/persona prompt
        temperature: Sampling temperature (0.0-2.0)
    """
    # PART 2a: Start history with ONE system message
    history = [{"role": "system", "content": system_prompt}]
    
    total_tokens_used = 0
    
    # PART 2b: Loop forever until user quits
    while True:
        try:
            # Read input from the user
            user_input = input("you > ").strip()
            
            # Exit on "quit" or "exit"
            if user_input.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break
            
            # Ignore empty inputs
            if not user_input:
                continue
            
            # Append user message to history
            history.append({"role": "user", "content": user_input})
            
            # PART 4: Call API with FULL history + temperature + error handling
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=history,
                    temperature=temperature,
                )
                
                # Extract assistant reply
                assistant_reply = response.choices[0].message.content
                
                # Print the reply
                print(f"bot > {assistant_reply}\n")
                
                # Append assistant message to history
                history.append({"role": "assistant", "content": assistant_reply})
                
                # PART 4: Token meter (rough estimation)
                input_tokens = sum(len(msg["content"]) for msg in history) // CHARS_PER_TOKEN
                output_tokens = len(assistant_reply) // CHARS_PER_TOKEN
                total_tokens_used += input_tokens + output_tokens
                
                print(f"[tokens this turn: ~{input_tokens + output_tokens} | total: ~{total_tokens_used}]\n")
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user.")
                break
            except Exception as e:
                print(f"Error calling API: {e}", file=sys.stderr)
                # Remove the failed user message from history
                history.pop()
                continue
                
        except KeyboardInterrupt:

            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


# ===========================================================================
# PART 3 — CLI flags (done for you — wire your functions in)
# ===========================================================================
def main():
    parser = argparse.ArgumentParser(description="AskBot — a tiny LLM CLI")
    parser.add_argument("--persona", default="You are a concise, helpful assistant.",
                        help="System prompt / persona")
    parser.add_argument("--temp", type=float, default=0.7,
                        help="Temperature 0.0–2.0")
    parser.add_argument("--once", metavar="PROMPT",
                        help="Ask a single question and exit")
    args = parser.parse_args()

    if args.once:
        print(ask_once(args.once))
    else:
        print(f"AskBot ready (model={MODEL}, temp={args.temp}). Type 'quit' to exit.")
        chat_loop(args.persona, args.temp)


if __name__ == "__main__":
    main()
