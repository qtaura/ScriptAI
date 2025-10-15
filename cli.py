#!/usr/bin/env python3
"""
ScriptAI CLI - Enterprise-Grade AI-Powered Code Generation Platform

A command-line tool that generates code snippets from natural language prompts
using various AI models including OpenAI GPT, HuggingFace StarCoder, and local models.

Usage:
  python cli.py -i                                                # Interactive mode
  python cli.py "Create a Python function to sort a list" -m openai  # Direct mode
  python cli.py --examples                                        # Show example prompts
  python cli.py --help                                            # Show help message

Commands (Interactive Mode):
  help                   Show available commands
  model <name>           Switch AI model (openai, huggingface, local)
  save <filename>        Save last generated code to file
  examples               Show example prompts
  clear                  Clear the screen
  history                Show command history
  exit, quit             Exit the program
"""

import argparse
import os
import sys
import json

try:
    import readline
except ImportError:
    # readline is not available on Windows
    pass

import platform
import textwrap
from datetime import datetime
from typing import Tuple, List, Optional, Dict, Any
from dotenv import load_dotenv
from security import SecurityManager

# Load environment variables
load_dotenv()

# Constants
VERSION = "0.1.0"
MAX_HISTORY = 10
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1500
CONFIG_DIR = os.path.expanduser("~/.scriptai")
HISTORY_FILE = os.path.join(CONFIG_DIR, "history.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Default to HuggingFace Inference API if OpenAI key not provided
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Example prompts for different programming tasks
EXAMPLE_PROMPTS = {
    "Python Data Processing": (
        "Create a Python function that reads a CSV file, "
        "filters rows where the 'age' column is greater than 30, "
        "and writes the result to a new CSV file."
    ),
    "JavaScript Frontend": (
        "Write a React component that displays a paginated list of items "
        "fetched from an API endpoint."
    ),
    "SQL Database": (
        "Create a SQL query that joins three tables (users, orders, products) "
        "and returns the total amount spent by each user on each product category."
    ),
    "API Development": (
        "Create a FastAPI endpoint that accepts user registration data, "
        "validates it, and stores it in a database."
    ),
    "Algorithm Implementation": (
        "Implement a depth-first search algorithm in Python for traversing a graph "
        "represented as an adjacency list."
    ),
    "Testing": (
        "Write a pytest test suite for a function that validates email addresses."
    ),
    "DevOps": (
        "Create a Docker Compose file for a web application with a Node.js backend, "
        "React frontend, and MongoDB database."
    ),
    "Data Science": (
        "Write a Python function using pandas and matplotlib to create a visualization "
        "of time series data with moving averages."
    ),
}


class CodeGenerator:
    """Base class for code generation models"""

    def __init__(
        self,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate code from prompt"""
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def format_code(code: str) -> str:
        """Format the generated code for display"""
        if not code:
            return ""

        # If code contains markdown code blocks, extract them
        if "```" in code:
            parts = code.split("```")
            # Find the first code block
            for i in range(1, len(parts)):
                if parts[i].strip() and not parts[i].startswith(
                    ("python", "javascript", "java", "cpp")
                ):
                    return parts[i].strip()
            # If we didn't find a suitable block, return the original with markers removed
            return code.replace("```", "").strip()

        return code.strip()


class OpenAIGenerator(CodeGenerator):
    """Generate code using OpenAI API"""

    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            import openai

            if not OPENAI_API_KEY:
                return (
                    None,
                    (
                        "OpenAI API key not found. "
                        "Please set the OPENAI_API_KEY environment variable."
                    ),
                )

            openai.api_key = OPENAI_API_KEY

            system_prompt = (
                "You are an expert programmer that generates clean, efficient, "
                "and well-documented code. "
                "Focus on providing only the code implementation "
                "with minimal explanation. "
                "Include helpful comments within the code "
                "to explain complex parts. "
                "If the language isn't specified, choose the most appropriate "
                "one for the task."
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            code = response.choices[0].message.content
            return self.format_code(code), None

        except ImportError:
            return (
                None,
                "OpenAI package not installed. Install it with: pip install openai",
            )
        except Exception as e:
            return None, f"Error with OpenAI API: {str(e)}"


class HuggingFaceGenerator(CodeGenerator):
    """Generate code using HuggingFace Inference API"""

    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            import requests

            if not HUGGINGFACE_API_KEY:
                return (
                    None,
                    (
                        "HuggingFace API key not found. "
                        "Please set the HUGGINGFACE_API_KEY environment variable."
                    ),
                )

            API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder"
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

            # Prepare the prompt for code generation
            full_prompt = f"Generate code for the following request: {prompt}\n\n```"

            response = requests.post(
                API_URL,
                headers=headers,
                json={
                    "inputs": full_prompt,
                    "parameters": {
                        "max_new_tokens": self.max_tokens,
                        "temperature": self.temperature,
                        "return_full_text": False,
                    },
                },
            )

            if response.status_code == 200:
                result = response.json()
                # Extract the generated code
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    return self.format_code(generated_text), None
                return "No code generated", None
            else:
                return None, f"Error: API returned status code {response.status_code}"

        except ImportError:
            return (
                None,
                "Requests package not installed. Install it with: pip install requests",
            )
        except Exception as e:
            return None, f"Error with HuggingFace API: {str(e)}"


class LocalModelGenerator(CodeGenerator):
    """Generate code using a local model"""

    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            prompt_clean = prompt.strip()
            if not prompt_clean:
                return None, "Empty prompt"

            # Simple language detection heuristics from prompt keywords
            lang = self._detect_language(prompt_clean)
            code = self._generate_stub(lang, prompt_clean)
            return code, None
        except Exception as e:
            return None, f"Local generator error: {str(e)}"

    def _detect_language(self, prompt: str) -> str:
        p = prompt.lower()
        if any(k in p for k in ["python", "pandas", "fastapi", "def "]):
            return "python"
        if any(k in p for k in ["react", "javascript", "node", "function "]):
            return "javascript"
        if any(k in p for k in ["sql", "select", "from", "where"]):
            return "sql"
        if any(k in p for k in ["html", "css", "<!doctype", "<html"]):
            return "html"
        return "python"

    def _generate_stub(self, lang: str, prompt: str) -> str:
        if lang == "python":
            return (
                "def generated_function(*args, **kwargs):\n"
                "    \"\"\"\n"
                f"    Generated locally based on prompt: {prompt}\n"
                "    Replace this stub with your implementation.\n"
                "    \"\"\"\n"
                "    # TODO: implement logic based on requirements above\n"
                "    return None\n"
            )
        if lang == "javascript":
            return (
                "// Generated locally based on prompt\n"
                f"// {prompt}\n"
                "export function generatedFunction(...args) {\n"
                "  // TODO: implement logic based on requirements above\n"
                "  return null;\n"
                "}\n"
            )
        if lang == "sql":
            return (
                "-- Generated locally based on prompt\n"
                f"-- {prompt}\n"
                "SELECT 1 AS placeholder;\n"
            )
        if lang == "html":
            return (
                "<!-- Generated locally based on prompt -->\n"
                f"<!-- {prompt} -->\n"
                "<!DOCTYPE html><html><head>"
                "<meta charset=\"utf-8\">"
                "<title>Generated</title>"
                "</head>\n"
                "<body>"
                "<div id=\"app\">Replace this stub with your implementation</div>"
                "</body></html>\n"
            )
        # Default to python
        return self._generate_stub("python", prompt)


class ScriptAICLI:
    """Main CLI application class"""

    def __init__(self):
        self.history = []
        self.last_generated_code = None
        self.config = self._load_config()
        self._setup_directories()

        # Validate environment on startup (API keys and config paths)
        try:
            self._validate_environment_on_startup()
        except Exception as _e:
            # Never fail startup due to validation; show a friendly note
            print(f"Warning: environment validation skipped due to: {str(_e)}")

        # Set default model based on available API keys
        if OPENAI_API_KEY:
            self.current_model = "openai"
        elif HUGGINGFACE_API_KEY:
            self.current_model = "huggingface"
        else:
            self.current_model = "local"

        # Initialize generators
        self.generators = {
            "openai": OpenAIGenerator(
                temperature=self.config.get("openai", {}).get(
                    "temperature", DEFAULT_TEMPERATURE
                ),
                max_tokens=self.config.get("openai", {}).get(
                    "max_tokens", DEFAULT_MAX_TOKENS
                ),
            ),
            "huggingface": HuggingFaceGenerator(
                temperature=self.config.get("huggingface", {}).get(
                    "temperature", DEFAULT_TEMPERATURE
                ),
                max_tokens=self.config.get("huggingface", {}).get(
                    "max_tokens", DEFAULT_MAX_TOKENS
                ),
            ),
            "local": LocalModelGenerator(
                temperature=self.config.get("local", {}).get(
                    "temperature", DEFAULT_TEMPERATURE
                ),
                max_tokens=self.config.get("local", {}).get(
                    "max_tokens", DEFAULT_MAX_TOKENS
                ),
            ),
        }

    def _setup_directories(self):
        """Create necessary directories if they don't exist"""
        if not os.path.exists(CONFIG_DIR):
            try:
                os.makedirs(CONFIG_DIR)
            except OSError as e:
                print(f"Warning: Could not create config directory: {e}")

    def _validate_environment_on_startup(self) -> None:
        """Validate environment configuration and ensure required paths exist.

        - Checks API keys for OpenAI and HuggingFace (format hints only)
        - Ensures config and history files exist (creates minimal defaults)
        """
        print("\n[Environment Check]")

        sm = SecurityManager()

        def _key_status(name: str, key: Optional[str]) -> str:
            if not key:
                return "missing"
            return "ok" if sm.validate_api_key(key) else "looks invalid"

        # Report API key status (non-fatal)
        print(f"- OPENAI_API_KEY: {_key_status('OPENAI_API_KEY', OPENAI_API_KEY)}")
        print(
            f"- HUGGINGFACE_API_KEY: {_key_status('HUGGINGFACE_API_KEY', HUGGINGFACE_API_KEY)}"
        )

        # Ensure config directory exists
        if not os.path.exists(CONFIG_DIR):
            try:
                os.makedirs(CONFIG_DIR)
                print(f"- Created config directory: {CONFIG_DIR}")
            except OSError as e:
                print(f"- Warning: Could not create config directory: {e}")

        # Create minimal defaults for config and history if missing
        default_config = {
            "openai": {
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS,
            },
            "huggingface": {
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS,
            },
            "local": {
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS,
            },
        }

        if not os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "w") as f:
                    json.dump(default_config, f, indent=2)
                print(f"- Initialized config file: {CONFIG_FILE}")
            except OSError as e:
                print(f"- Warning: Could not initialize config file: {e}")
        else:
            print(f"- Config file ready: {CONFIG_FILE}")

        if not os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "w") as f:
                    json.dump([], f)
                print(f"- Initialized history file: {HISTORY_FILE}")
            except OSError as e:
                print(f"- Warning: Could not initialize history file: {e}")
        else:
            print(f"- History file ready: {HISTORY_FILE}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "openai": {
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS,
            },
            "huggingface": {
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS,
            },
            "local": {
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS,
            },
        }

        if not os.path.exists(CONFIG_FILE):
            return default_config

        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config if isinstance(config, dict) else default_config
        except (json.JSONDecodeError, OSError):
            return default_config

    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2)
        except OSError as e:
            print(f"Warning: Could not save config: {e}")

    def _add_to_history(self, prompt: str, model: str):
        """Add a prompt to history"""
        self.history.append(
            {"timestamp": datetime.now().isoformat(), "prompt": prompt, "model": model}
        )

        # Trim history to maximum size
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]

    def _save_history(self):
        """Save command history to file"""
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(self.history, f, indent=2)
        except OSError as e:
            print(f"Warning: Could not save history: {e}")

    def _load_history(self):
        """Load command history from file"""
        if not os.path.exists(HISTORY_FILE):
            return

        try:
            with open(HISTORY_FILE, "r") as f:
                self.history = json.load(f)
        except (json.JSONDecodeError, OSError):
            self.history = []

    def _clear_screen(self):
        """Clear the terminal screen"""
        os_name = platform.system()
        if os_name == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    def _print_header(self):
        """Print the application header"""
        print("\n" + "=" * 80)
        print(f"ScriptAI CLI v{VERSION} - Enterprise-Grade AI-Powered Code Generation")
        print("=" * 80)
        print(f"Current Model: {self.current_model}")
        print("Type 'help' to see available commands")
        print("=" * 80 + "\n")

    def _print_help(self):
        """Print help information"""
        help_text = """
Available Commands:
  help                   Show this help message
  model <name>           Switch AI model (openai, huggingface, local)
  save <filename>        Save last generated code to file
  examples               Show example prompts
  clear                  Clear the screen
  history                Show command history
  exit, quit             Exit the program

Any other input will be treated as a prompt for code generation.
        """
        print(textwrap.dedent(help_text))

    def _print_examples(self):
        """Print example prompts"""
        print("\nExample Prompts:")
        print("=" * 80)
        for category, prompt in EXAMPLE_PROMPTS.items():
            print(f"\n{category}:")
            print(f"  {prompt}")
        print("\n" + "=" * 80)

    def _show_history(self):
        """Show command history"""
        if not self.history:
            print("No history available.")
            return

        print("\nCommand History:")
        print("=" * 80)
        for i, entry in enumerate(self.history, 1):
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            print(f"{i}. [{timestamp}] [{entry['model']}] {entry['prompt'][:50]}...")
        print("=" * 80)

    def _save_code_to_file(self, filename: str) -> bool:
        """Save generated code to file"""
        if not self.last_generated_code:
            print("No code has been generated yet.")
            return False

        try:
            with open(filename, "w") as f:
                f.write(self.last_generated_code)
            print(f"Code saved to {filename}")
            return True
        except OSError as e:
            print(f"Error saving file: {e}")
            return False

    def _switch_model(self, model_name: str) -> bool:
        """Switch the current AI model with validation and helpful recovery"""
        requested = (model_name or "").strip().lower()

        # Validate model exists
        if requested not in self.generators:
            print(f"Unknown model: {requested}")
            print(f"Available models: {', '.join(self.generators.keys())}")
            print(f"Staying on current model: {self.current_model}")
            return False

        # Validate required credentials for remote providers
        if requested == "openai" and not OPENAI_API_KEY:
            print("OpenAI API key not configured; cannot switch to 'openai'.")
            print("Tip: set OPENAI_API_KEY in your .env or environment.")
            print(f"Staying on current model: {self.current_model}")
            return False
        if requested == "huggingface" and not HUGGINGFACE_API_KEY:
            print("HuggingFace API key not configured; cannot switch to 'huggingface'.")
            print("Tip: set HUGGINGFACE_API_KEY in your .env or environment.")
            print(f"Staying on current model: {self.current_model}")
            return False

        self.current_model = requested
        print(f"Switched to model: {self.current_model}")
        return True

    def _generate_code(self, prompt: str) -> bool:
        """Generate code from prompt"""
        if not prompt.strip():
            return False

        print(f"\nGenerating code using {self.current_model}...")

        generator = self.generators.get(self.current_model)
        if not generator:
            print(f"Error: Model {self.current_model} not available.")
            return False

        code, error = generator.generate(prompt)

        if error:
            print(f"Error: {error}")
            if "API key not found" in error:
                print(
                    "To set up your API key, create a .env file with "
                    f"{self.current_model.upper()}_API_KEY=your_key_here"
                )
            return False

        self._add_to_history(prompt, self.current_model)
        self.last_generated_code = code

        print("\n" + "=" * 40 + " GENERATED CODE " + "=" * 40)
        print(code)
        print("=" * 90)

        return True

    def run_interactive_mode(self):
        """Run the CLI in interactive mode"""
        self._load_history()
        self._print_header()

        while True:
            try:
                user_input = input("\nScriptAI> ").strip()

                if not user_input:
                    continue

                # Process commands
                if user_input.lower() in ["exit", "quit"]:
                    break
                elif user_input.lower() == "help":
                    self._print_help()
                elif user_input.lower() == "examples":
                    self._print_examples()
                elif user_input.lower() == "clear":
                    self._clear_screen()
                    self._print_header()
                elif user_input.lower() == "history":
                    self._show_history()
                elif user_input.lower().startswith("save "):
                    filename = user_input[5:].strip()
                    if filename:
                        self._save_code_to_file(filename)
                elif user_input.lower().startswith("model "):
                    model_name = user_input[6:].strip().lower()
                    self._switch_model(model_name)
                else:
                    # Treat as code generation prompt
                    self._generate_code(user_input)

            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                continue
            except EOFError:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"An error occurred: {str(e)}")

        # Save history before exiting
        self._save_history()
        print("\nThank you for using ScriptAI CLI!")

    def run_direct_mode(self, prompt: str, output_file: Optional[str] = None):
        """Run the CLI in direct mode with a single prompt"""
        success = self._generate_code(prompt)

        if success and output_file:
            self._save_code_to_file(output_file)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ScriptAI - Enterprise-Grade AI-Powered Code Generation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
        Examples:
          python cli.py -i                                                # Interactive mode
          python cli.py "Create a Python function to sort a list" -m openai  # Direct mode
          python cli.py --examples                                        # Show example prompts
        """
        ),
    )

    parser.add_argument(
        "prompt", nargs="?", help="The prompt describing the code you want to generate"
    )
    parser.add_argument("--file", "-f", help="Save the generated code to this file")
    parser.add_argument(
        "--model",
        "-m",
        # Accept any string; validate gracefully to avoid argparse exiting on invalid choices
        default="openai" if OPENAI_API_KEY else "huggingface",
        help="Model to use for code generation (openai|huggingface|local)",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument("--examples", action="store_true", help="Show example prompts")
    parser.add_argument(
        "--version", "-v", action="version", version=f"ScriptAI CLI v{VERSION}"
    )

    args = parser.parse_args()

    cli = ScriptAICLI()

    # Set the model from command line argument; validate and recover gracefully
    if args.model:
        if not cli._switch_model(args.model):
            print(
                f"Invalid or unavailable model '{args.model}'. Using default '{cli.current_model}'."
            )

    # Show examples if requested
    if args.examples:
        cli._print_examples()
        return

    # Interactive mode
    if args.interactive:
        cli.run_interactive_mode()
        return

    # Direct mode
    if not args.prompt:
        parser.print_help()
        return

    cli.run_direct_mode(args.prompt, args.file)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)
