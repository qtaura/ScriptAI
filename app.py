from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    # Pass available models to the template
    models = []
    if OPENAI_API_KEY:
        models.append({"id": "openai", "name": "OpenAI GPT-3.5"})
    if HUGGINGFACE_API_KEY:
        models.append({"id": "huggingface", "name": "HuggingFace StarCoder"})
    models.append({"id": "local", "name": "Local Model (Placeholder)"})
    
    return render_template('index.html', models=models)

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
    return "// This is a placeholder for local model generation.\n// In a real implementation, this would use a local model like llama.cpp\n\n// Example code based on your prompt:\nfunction example() {\n  console.log('Local model generation would go here');\n}", None

@app.route('/generate', methods=['POST'])
def generate_code():
    # Get the prompt and model from the request
    data = request.get_json()
    prompt = data.get('prompt', '')
    model = data.get('model', 'openai')
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    # Generate code based on selected model
    if model == "openai":
        code, error = generate_with_openai(prompt)
    elif model == "huggingface":
        code, error = generate_with_huggingface(prompt)
    elif model == "local":
        code, error = generate_with_local_model(prompt)
    else:
        return jsonify({"error": f"Unknown model: {model}"}), 400
    
    if error:
        return jsonify({"error": error}), 500
    
    return jsonify({"code": code})

if __name__ == '__main__':
    app.run(debug=True)