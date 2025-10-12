#!/usr/bin/env python3
"""
AI Code Assistant CLI
A command-line tool that generates code snippets from natural language prompts.
"""

import argparse
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default to HuggingFace Inference API if OpenAI key not provided
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

def generate_with_openai(prompt):
    """Generate code using OpenAI API"""
    import openai
    
    if not OPENAI_API_KEY:
        return None, "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    
    openai.api_key = OPENAI_API_KEY
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates code based on user requirements. Provide only the code with minimal explanation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content, None
    except Exception as e:
        return None, f"Error with OpenAI API: {str(e)}"

def generate_with_huggingface(prompt):
    """Generate code using HuggingFace Inference API (free alternative)"""
    import requests
    
    if not HUGGINGFACE_API_KEY:
        return None, "HuggingFace API key not found. Please set the HUGGINGFACE_API_KEY environment variable."
    
    API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    # Prepare the prompt for code generation
    full_prompt = f"Generate code for the following request: {prompt}\n\n```"
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": full_prompt, "parameters": {"max_new_tokens": 500, "return_full_text": False}}
        )
        
        if response.status_code == 200:
            result = response.json()
            # Extract the generated code
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                # Clean up the response to extract just the code
                if "```" in generated_text:
                    # Extract code between backticks if present
                    code_parts = generated_text.split("```")
                    if len(code_parts) >= 2:
                        return code_parts[1].strip(), None
                return generated_text.strip(), None
            return "No code generated", None
        else:
            return None, f"Error: API returned status code {response.status_code}"
    except Exception as e:
        return None, f"Error with HuggingFace API: {str(e)}"

def generate_with_local_model(prompt):
    """Generate code using a local model (placeholder for future implementation)"""
    # This is a placeholder for future implementation with local models
    return None, "Local model generation not implemented yet. Consider using llama.cpp or similar for local inference."

def main():
    parser = argparse.ArgumentParser(description="Generate code from natural language prompts")
    parser.add_argument("prompt", nargs="?", help="The prompt describing the code you want to generate")
    parser.add_argument("--file", "-f", help="Save the generated code to this file")
    parser.add_argument("--model", "-m", choices=["openai", "huggingface", "local"], 
                        default="openai" if OPENAI_API_KEY else "huggingface",
                        help="Model to use for code generation")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        print("AI Code Assistant CLI - Interactive Mode")
        print("Type 'exit' or 'quit' to end the session")
        print("Type 'model openai|huggingface|local' to change the model")
        
        current_model = args.model
        print(f"Using model: {current_model}")
        
        while True:
            try:
                user_input = input("\nEnter your prompt: ")
                
                if user_input.lower() in ["exit", "quit"]:
                    break
                
                if user_input.lower().startswith("model "):
                    model_name = user_input.lower().split(" ")[1]
                    if model_name in ["openai", "huggingface", "local"]:
                        current_model = model_name
                        print(f"Switched to model: {current_model}")
                    else:
                        print(f"Unknown model: {model_name}")
                    continue
                
                if not user_input.strip():
                    continue
                
                print("\nGenerating code...")
                
                if current_model == "openai":
                    code, error = generate_with_openai(user_input)
                elif current_model == "huggingface":
                    code, error = generate_with_huggingface(user_input)
                elif current_model == "local":
                    code, error = generate_with_local_model(user_input)
                
                if error:
                    print(f"Error: {error}")
                    continue
                
                print("\n" + "=" * 40 + " GENERATED CODE " + "=" * 40)
                print(code)
                print("=" * 90)
                
                save_option = input("\nSave this code to a file? (y/n): ")
                if save_option.lower() == 'y':
                    filename = input("Enter filename: ")
                    if filename:
                        with open(filename, 'w') as f:
                            f.write(code)
                        print(f"Code saved to {filename}")
            
            except KeyboardInterrupt:
                print("\nExiting interactive mode...")
                break
            except Exception as e:
                print(f"An error occurred: {str(e)}")
        
        print("Thank you for using AI Code Assistant CLI!")
        return
    
    # Non-interactive mode
    if not args.prompt:
        parser.print_help()
        return
    
    print(f"Generating code using {args.model}...")
    
    if args.model == "openai":
        code, error = generate_with_openai(args.prompt)
    elif args.model == "huggingface":
        code, error = generate_with_huggingface(args.prompt)
    elif args.model == "local":
        code, error = generate_with_local_model(args.prompt)
    
    if error:
        print(f"Error: {error}")
        return
    
    if args.file:
        with open(args.file, 'w') as f:
            f.write(code)
        print(f"Code saved to {args.file}")
    else:
        print("\n" + "=" * 40 + " GENERATED CODE " + "=" * 40)
        print(code)
        print("=" * 90)

if __name__ == "__main__":
    main()