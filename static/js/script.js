document.addEventListener('DOMContentLoaded', function() {
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const codeOutput = document.getElementById('code-output');
    const codeContainer = document.getElementById('code-container');
    const copyBtn = document.getElementById('copy-btn');
    const saveBtn = document.getElementById('save-btn');
    const modelSelect = document.getElementById('model-select');
    const languageSelect = document.getElementById('language-select');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');

    // Function to detect language from code
    function detectLanguage(code) {
        const firstLine = code.trim().split('\n')[0].toLowerCase();
        
        if (firstLine.includes('python') || firstLine.includes('def ') || firstLine.includes('import ') || code.includes('def ') || code.includes('class ') && code.includes(':')) {
            return 'python';
        } else if (firstLine.includes('javascript') || firstLine.includes('function') || firstLine.includes('const ') || code.includes('function') || code.includes('const ') || code.includes('let ')) {
            return 'javascript';
        } else if (firstLine.includes('html') || firstLine.includes('<!doctype') || firstLine.includes('<html') || code.includes('<html') || code.includes('<div')) {
            return 'html';
        } else if (firstLine.includes('java') || firstLine.includes('class ') || firstLine.includes('public ') || code.includes('public class') || code.includes('private ')) {
            return 'java';
        } else if (code.includes('using System;') || code.includes('namespace ') || code.includes('public class') && code.includes('{')) {
            return 'csharp';
        } else if (code.includes('#include') || code.includes('int main(') || code.includes('std::')) {
            return 'cpp';
        } else if (code.includes('<?php') || code.includes('function ') && code.includes('$')) {
            return 'php';
        } else if (code.includes('func ') && code.includes('package ')) {
            return 'go';
        } else if (code.includes('fn ') && code.includes('let mut ') || code.includes('impl ')) {
            return 'rust';
        } else if (code.includes('SELECT ') || code.includes('FROM ') || code.includes('WHERE ')) {
            return 'sql';
        } else if (code.includes('#!/bin/bash') || code.includes('echo ') || code.includes('if [')) {
            return 'bash';
        } else if (code.includes('def ') || code.includes('end') || code.includes('require ')) {
            return 'ruby';
        } else if (code.includes('body {') || code.includes('@media') || code.includes('.class')) {
            return 'css';
        }
        
        return 'javascript'; // Default
    }

    // Function to update code with syntax highlighting
    function updateCodeWithHighlighting(code) {
        // Detect language
        const detectedLanguage = detectLanguage(code);
        
        // Update language selector
        languageSelect.value = detectedLanguage;
        
        // Update code element class for Prism
        codeOutput.className = `language-${detectedLanguage}`;
        
        // Set the code text
        codeOutput.textContent = code;
        
        // Apply Prism highlighting
        Prism.highlightElement(codeOutput);
    }

    // Language selector change event
    languageSelect.addEventListener('change', function() {
        const selectedLanguage = languageSelect.value;
        const currentCode = codeOutput.textContent;
        
        if (currentCode && currentCode !== 'Your generated code will appear here...') {
            codeOutput.className = `language-${selectedLanguage}`;
            Prism.highlightElement(codeOutput);
        }
    });

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
        codeOutput.className = 'language-plaintext';
        
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
                updateCodeWithHighlighting(data.code);
            } else {
                showError(data.error || 'Failed to generate code. Please try again.');
                codeOutput.textContent = 'Error generating code. Please try again.';
            }
        } catch (error) {
            showError('An error occurred while connecting to the server.');
            console.error('Error:', error);
            codeOutput.textContent = 'Connection error. Please try again.';
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
            // Get file extension based on selected language
            const language = languageSelect.value;
            let fileExtension = '.txt';
            
            // Map language to file extension
            const extensionMap = {
                'javascript': '.js',
                'python': '.py',
                'java': '.java',
                'csharp': '.cs',
                'cpp': '.cpp',
                'php': '.php',
                'ruby': '.rb',
                'go': '.go',
                'rust': '.rs',
                'sql': '.sql',
                'html': '.html',
                'css': '.css',
                'bash': '.sh'
            };
            
            if (extensionMap[language]) {
                fileExtension = extensionMap[language];
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