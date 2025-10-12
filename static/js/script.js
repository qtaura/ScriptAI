document.addEventListener('DOMContentLoaded', function() {
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const codeOutput = document.getElementById('code-output');
    const copyBtn = document.getElementById('copy-btn');
    const saveBtn = document.getElementById('save-btn');
    const modelSelect = document.getElementById('model-select');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');

    // Generate code when button is clicked
    generateBtn.addEventListener('click', async function() {
        const prompt = promptInput.value.trim();
        const selectedModel = modelSelect.value;
        
        if (!prompt) {
            showError('Please enter a prompt to generate code.');
            return;
        }
        
        // Show loading indicator
        loading.classList.remove('hidden');
        errorMessage.classList.add('hidden');
        codeOutput.textContent = 'Generating...';
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    prompt: prompt,
                    model: selectedModel
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                codeOutput.textContent = data.code;
            } else {
                showError(data.error || 'Failed to generate code. Please try again.');
            }
        } catch (error) {
            showError('An error occurred while connecting to the server.');
            console.error('Error:', error);
        } finally {
            loading.classList.add('hidden');
        }
    });
    
    // Copy generated code to clipboard
    copyBtn.addEventListener('click', function() {
        const codeText = codeOutput.textContent;
        
        if (codeText && codeText !== 'Your generated code will appear here...') {
            navigator.clipboard.writeText(codeText)
                .then(() => {
                    const originalText = copyBtn.textContent;
                    copyBtn.textContent = 'Copied!';
                    setTimeout(() => {
                        copyBtn.textContent = originalText;
                    }, 2000);
                })
                .catch(err => {
                    showError('Failed to copy code to clipboard.');
                    console.error('Error copying text:', err);
                });
        }
    });
    
    // Save generated code to a file
    saveBtn.addEventListener('click', function() {
        const codeText = codeOutput.textContent;
        
        if (codeText && codeText !== 'Your generated code will appear here...') {
            // Detect language to set file extension
            let fileExtension = '.txt';
            const firstLine = codeText.trim().split('\n')[0].toLowerCase();
            
            if (firstLine.includes('python') || firstLine.includes('def ') || firstLine.includes('import ')) {
                fileExtension = '.py';
            } else if (firstLine.includes('javascript') || firstLine.includes('function') || firstLine.includes('const ')) {
                fileExtension = '.js';
            } else if (firstLine.includes('html') || firstLine.includes('<!doctype') || firstLine.includes('<html')) {
                fileExtension = '.html';
            } else if (firstLine.includes('java') || firstLine.includes('class ') || firstLine.includes('public ')) {
                fileExtension = '.java';
            }
            
            // Create a blob and download link
            const blob = new Blob([codeText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            
            a.href = url;
            a.download = `generated_code${fileExtension}`;
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }, 100);
        }
    });
    
    // Helper function to show error messages
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }
    
    // Add keyboard shortcut (Ctrl+Enter) to generate code
    promptInput.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            generateBtn.click();
        }
    });
});