import * as React from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader } from './ui/card';
import { Select } from './ui/select';
import { Copy, Download } from 'lucide-react';

type Model = { id: string; name: string };

const languages = [
  'javascript', 'python', 'java', 'csharp', 'cpp', 'php', 'ruby', 'go', 'rust', 'sql', 'html', 'css', 'bash', 'plaintext',
];

export function Generator() {
  const [models, setModels] = React.useState<Model[]>([]);
  const [model, setModel] = React.useState<string>('local');
  const [prompt, setPrompt] = React.useState<string>('');
  const [language, setLanguage] = React.useState<string>('plaintext');
  const [code, setCode] = React.useState<string>('Your generated code will appear here…');
  const [loading, setLoading] = React.useState<boolean>(false);
  const [notice, setNotice] = React.useState<{ type: 'error' | 'success' | 'info'; message: string } | null>(null);

  React.useEffect(() => {
    fetch('/models')
      .then((r) => r.json())
      .then((ms: Model[]) => {
        setModels(ms);
        if (ms[0]) setModel(ms[0].id);
      })
      .catch(() => {
        setModels([{ id: 'local', name: 'Local Model (Placeholder)' }]);
        setModel('local');
      });
  }, []);

  async function onGenerate() {
    if (!prompt.trim()) {
      setNotice({ type: 'error', message: 'Please enter a prompt to generate code.' });
      return;
    }
    setLoading(true);
    setNotice(null);
    setCode('Generating…');
    try {
      const res = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, model }),
      });
      const data = await res.json();
      if (res.ok) {
        setCode(data.code);
        setNotice({ type: 'success', message: 'Code generated successfully.' });
      } else {
        setNotice({ type: 'error', message: data.error || 'Failed to generate code.' });
        setCode('Error generating code. Please try again.');
      }
    } catch (e) {
      console.error(e);
      setNotice({ type: 'error', message: 'Connection error. Please try again.' });
      setCode('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function copyCode() {
    navigator.clipboard.writeText(code).then(() => {
      setNotice({ type: 'success', message: 'Code copied to clipboard.' });
    });
  }

  function downloadCode() {
    const map: Record<string, string> = {
      javascript: '.js', python: '.py', java: '.java', csharp: '.cs', cpp: '.cpp', php: '.php', ruby: '.rb', go: '.go', rust: '.rs', sql: '.sql', html: '.html', css: '.css', bash: '.sh', plaintext: '.txt',
    };
    const ext = map[language] || '.txt';
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `generated_code${ext}`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
    setNotice({ type: 'success', message: `Downloaded generated_code${ext}` });
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <img src="/static/images/logo.svg" alt="Logo" className="h-8 w-8" />
          <div>
            <h1 className="text-xl font-semibold">ScriptAI</h1>
            <p className="text-sm text-neutral-600">AI-Powered Code Generation</p>
          </div>
        </div>
        <div>
          <a href="/metrics-json" target="_blank" className="text-sm text-neutral-700 hover:underline">Metrics</a>
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-2xl font-semibold">Ship code faster with confidence</h2>
        <p className="text-neutral-600">A clean, professional interface for AI-powered code generation. Fast, reliable, and built for real teams.</p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium">Generate Code</h3>
            <div className="text-sm text-neutral-600">Model: {models.find((m) => m.id === model)?.name ?? '—'}</div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            <div className="grid gap-1">
              <label htmlFor="model" className="text-sm text-neutral-700">Model</label>
              <Select id="model" value={model} onChange={(e) => setModel(e.target.value)}>
                {models.map((m) => (
                  <option key={m.id} value={m.id}>{m.name}</option>
                ))}
              </Select>
            </div>

            <div className="grid gap-1">
              <label htmlFor="prompt" className="text-sm text-neutral-700">Prompt</label>
              <textarea
                id="prompt"
                rows={8}
                className="w-full rounded-md border border-neutral-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-400"
                placeholder="e.g., Write a Python function that calculates the Fibonacci sequence"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </div>

            <div>
              <Button variant="primary" onClick={onGenerate} disabled={loading}>
                {loading ? 'Generating…' : 'Generate Code'}
              </Button>
            </div>

            {notice && (
              <div
                className={
                  notice.type === 'error'
                    ? 'rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-800'
                    : notice.type === 'success'
                    ? 'rounded-md border border-green-300 bg-green-50 p-3 text-sm text-green-800'
                    : 'rounded-md border border-neutral-300 bg-neutral-50 p-3 text-sm text-neutral-800'
                }
              >
                {notice.message}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium">Output</h3>
            <div className="flex items-center gap-2">
              <label htmlFor="lang" className="text-sm text-neutral-700">Language</label>
              <Select id="lang" value={language} onChange={(e) => setLanguage(e.target.value)}>
                {languages.map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <pre className="rounded-md border border-neutral-200 bg-neutral-50 p-3 overflow-auto text-sm">
            <code>{code}</code>
          </pre>
          <div className="mt-3 flex gap-2">
            <Button variant="outline" onClick={copyCode}><Copy className="mr-2 h-4 w-4" /> Copy</Button>
            <Button variant="outline" onClick={downloadCode}><Download className="mr-2 h-4 w-4" /> Download</Button>
            <Button variant="ghost" onClick={() => window.open('/performance', '_blank')}>Performance</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}