import { useEffect, useRef, useState } from "react";
import { Button } from "./ui/button";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";
import { Textarea } from "./ui/textarea";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Badge } from "./ui/badge";
import {
  Copy,
  Download,
  Sparkles,
  Code2,
  Check,
  Loader2,
} from "lucide-react";
import Prism from "prismjs";
import "prismjs/themes/prism.css";
import { SessionAnalytics } from "./SessionAnalytics";

export function CodeGenerator() {
  const [prompt, setPrompt] = useState("");
  const [model, setModel] = useState("local");
  const [language, setLanguage] = useState("python");
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [models, setModels] = useState<{ id: string; name: string }[]>([]);
  const [profiles, setProfiles] = useState<Record<string, { speed?: string; quality?: string; cost?: string; badge?: string; available?: boolean }>>({});
  const [availableIds, setAvailableIds] = useState<string[]>([]);
  const [generatedCode, setGeneratedCode] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [isModelOpen, setIsModelOpen] = useState(false);
  const [modelError, setModelError] = useState<string>("");

  useEffect(() => {
    // Dynamic Model Registry: prefer backend profiles, fallback to JSON config; filter by server availability
    const loadProfiles = fetch("/model-profiles")
      .then((r) => r.json())
      .then((data: { models?: Array<any> }) => {
        const items = Array.isArray(data?.models) ? data.models : [];
        const mapped: Record<string, { speed?: string; quality?: string; cost?: string; badge?: string; available?: boolean }> = {};
        items.forEach((m) => {
          const id = String(m?.id || "");
          if (!id) return;
          mapped[id] = {
            speed: typeof m?.speed === "string" ? m.speed : undefined,
            quality: typeof m?.quality === "string" ? m.quality : undefined,
            cost: typeof m?.cost === "string" ? m.cost : undefined,
            badge: typeof m?.badge === "string" ? m.badge : undefined,
            available: typeof m?.available === "boolean" ? m.available : undefined,
          };
        });
        return mapped;
      })
      .catch(() => ({}));

    const loadConfig = fetch("/modelCards.json")
      .then((r) => r.json())
      .then((data: { models?: { id?: string; name?: string }[] }) => {
        const items = Array.isArray(data?.models) ? data.models : [];
        const mapped = items
          .map((m) => ({ id: String(m.id || ""), name: String(m.name || "") }))
          .filter((m) => m.id && m.name);
        return mapped;
      })
      .catch(() =>
        // Fallback to SPA-served path when Flask serves UI from /ui/*
        fetch("/ui/modelCards.json")
          .then((r) => r.json())
          .then((data: { models?: { id?: string; name?: string }[] }) => {
            const items = Array.isArray(data?.models) ? data.models : [];
            const mapped = items
              .map((m) => ({ id: String(m.id || ""), name: String(m.name || "") }))
              .filter((m) => m.id && m.name);
            return mapped;
          })
          .catch(() => [])
      );

    const loadAvailable = fetch("/models")
      .then((r) => r.json())
      .then((ms: Array<{ id?: string; name?: string } | string>) => {
        const toId = (m: { id?: string; name?: string } | string) => {
          if (typeof m === "string") {
            const n = m.toLowerCase();
            if (n.includes("openai")) return "openai";
            if (n.includes("starcoder") || n.includes("huggingface")) return "huggingface";
            if (n.includes("anthropic") || n.includes("claude")) return "anthropic";
            if (n.includes("gemini") || n.includes("google")) return "gemini";
            if (n.includes("local")) return "local";
            return "";
          }
          const id = (m && typeof m.id === "string" && m.id) ? m.id : "";
          if (id) return id;
          const name = (m && typeof m.name === "string" && m.name) ? m.name.toLowerCase() : "";
          if (name.includes("openai")) return "openai";
          if (name.includes("starcoder") || name.includes("huggingface")) return "huggingface";
          if (name.includes("anthropic") || name.includes("claude")) return "anthropic";
          if (name.includes("gemini") || name.includes("google")) return "gemini";
          if (name.includes("local")) return "local";
          return "";
        };
        const ids = Array.isArray(ms) ? ms.map(toId).filter(Boolean) : [];
        return ids;
      })
      .catch(() => []);

    Promise.all([loadProfiles, loadConfig, loadAvailable])
      .then(([loadedProfiles, configModels, ids]) => {
        // Preserve config-defined display names but mark availability separately
        setAvailableIds(ids);
        if (loadedProfiles && Object.keys(loadedProfiles).length > 0) {
          setProfiles(loadedProfiles);
        }
        let finalModels = configModels;
        if (finalModels.length === 0 && ids.length > 0) {
          // Fallback to server list names when no config
          finalModels = ids.map((id) => ({ id, name: id }));
          setModelError("No config found. Using server model list.");
        }
        if (finalModels.length === 0) {
          // Fallback to local placeholder
          finalModels = [{ id: "local", name: "Local Model (Placeholder)" }];
          setModelError(
            "Failed to load models from config and server. Using placeholder.",
          );
        }
        setModels(finalModels);
        // Choose first available model if present, otherwise prefer local
        const availableDefault = finalModels.find((m) => ids.includes(m.id));
        const defaultModel = availableDefault || finalModels.find((m) => m.id === "local") || finalModels[0];
        if (defaultModel) setModel(defaultModel.id);
        // Inform about disabled items if some config models aren’t available
        if (finalModels.some((m) => !ids.includes(m.id))) {
          setModelError("Some models require API keys and are disabled until configured.");
        }
      })
      .catch(() => {
        setModels([{ id: "local", name: "Local Model (Placeholder)" }]);
        setModel("local");
        setModelError("Unexpected error loading model registry. Using placeholder.");
      });
  }, []);

  const exampleCode = {
    python: `import pandas as pd

def filter_csv_by_age(input_file, output_file, min_age=30):
    """
    Read a CSV file, filter rows where age > min_age, and save to new file.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
        min_age (int): Minimum age threshold (default: 30)
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        
        # Filter rows where age > min_age
        filtered_df = df[df['age'] > min_age]
        
        # Write filtered data to new CSV file
        filtered_df.to_csv(output_file, index=False)
        
        print(f"Filtered {len(filtered_df)} rows and saved to {output_file}")
        return filtered_df
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        return None
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None`,
    javascript: `async function fetchPaginatedData(apiUrl, page = 1, limit = 10) {
  try {
    const response = await fetch(\`\${apiUrl}?page=\${page}&limit=\${limit}\`);
    
    if (!response.ok) {
      throw new Error(\`HTTP error! status: \${response.status}\`);
    }
    
    const data = await response.json();
    return {
      items: data.items || [],
      total: data.total || 0,
      page: page,
      totalPages: Math.ceil((data.total || 0) / limit)
    };
  } catch (error) {
    console.error('Error fetching data:', error);
    return null;
  }
}`,
    sql: `SELECT 
    u.user_id,
    u.username,
    p.category,
    SUM(o.quantity * p.price) as total_spent
FROM users u
INNER JOIN orders o ON u.user_id = o.user_id
INNER JOIN products p ON o.product_id = p.product_id
GROUP BY u.user_id, u.username, p.category
ORDER BY u.username, p.category;`,
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    // Prevent generating with a model the server cannot handle
    if (availableIds.length > 0 && !availableIds.includes(model)) {
      setErrorMessage("Selected model is not available. Configure API keys and try again.");
      return;
    }
    setIsGenerating(true);
    setErrorMessage("");
    setGeneratedCode("");
    try {
      const res = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, model, language }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        const msg = (body && body.error) || `Request failed (${res.status})`;
        setErrorMessage(msg);
      } else {
        const code = body && body.code ? String(body.code) : "";
        setGeneratedCode(code || "");
      }
    } catch (e: any) {
      setErrorMessage(e?.message || "Network error");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    const fallback = exampleCode[language as keyof typeof exampleCode] || exampleCode.python;
    const code = generatedCode || fallback;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const displayCode = generatedCode || (exampleCode[language as keyof typeof exampleCode] || exampleCode.python);

  const codeRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const lang = (language || "").toLowerCase();
    const loadLanguage = async () => {
      try {
        if (lang === "python") {
          await import("prismjs/components/prism-python");
        } else if (lang === "javascript" || lang === "js") {
          await import("prismjs/components/prism-javascript");
        } else if (lang === "typescript" || lang === "ts") {
          await import("prismjs/components/prism-typescript");
        } else if (lang === "bash" || lang === "sh" || lang === "shell") {
          await import("prismjs/components/prism-bash");
        } else if (lang === "sql") {
          await import("prismjs/components/prism-sql");
        } else if (lang === "json") {
          await import("prismjs/components/prism-json");
        } else if (lang === "go" || lang === "golang") {
          await import("prismjs/components/prism-go");
        } else if (lang === "rust" || lang === "rs") {
          await import("prismjs/components/prism-rust");
        } else if (lang === "java") {
          await import("prismjs/components/prism-java");
        } else if (lang === "csharp" || lang === "cs") {
          await import("prismjs/components/prism-csharp");
        }
      } catch {
        // ignore missing language component; Prism will fall back
      } finally {
        if (codeRef.current) {
          Prism.highlightElement(codeRef.current);
        }
      }
    };
    loadLanguage();
  }, [displayCode, language]);

  const examples = [
    "Python function to scrape website data",
    "React component with API pagination",
    "SQL query joining multiple tables",
    "Bash script for file processing",
  ];

  return (
    <section id="generator" className="border-b py-16 md:py-20">
      <div className="container px-4 md:px-6">
        <div className="mb-12 text-center">
          <h2 className="mb-3">Try the Code Generator</h2>
          <p className="text-muted-foreground">
            Generate production-ready code from natural language descriptions
          </p>
        </div>

        <div className="mx-auto max-w-6xl">
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Input Panel */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code2 className="h-5 w-5" />
                  Input Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {modelError && (
                  <Alert variant="destructive">
                    <AlertTitle>Model Load Error</AlertTitle>
                    <AlertDescription>
                      {modelError}
                    </AlertDescription>
                  </Alert>
                )}
                <div className="space-y-2">
                  <label className="text-sm">Prompt</label>
                  <Textarea
                    placeholder="Describe what you want to create..."
                    className="min-h-[160px] resize-none font-mono text-sm"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                  />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className={`space-y-2 ${isModelOpen ? "pb-16" : ""}`}>
                    <label className="text-sm">AI Model</label>
                    <Select value={model} onValueChange={setModel} open={isModelOpen} onOpenChange={setIsModelOpen}>
                      <SelectTrigger className="font-mono">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {models.length === 0 ? (
                          <SelectItem value="local">Local Model (Placeholder)</SelectItem>
                        ) : (
                          models.map((m) => {
                            const available = availableIds.includes(m.id);
                            const label = available ? m.name : `${m.name} (requires key)`;
                            return (
                              <SelectItem key={m.id} value={m.id} disabled={!available}>
                                <div className="flex flex-col gap-1">
                                  <div>{label}</div>
                                  <div className="grid grid-cols-3 gap-2 text-[10px] text-muted-foreground">
                                    <div>
                                      <span className="mr-1">Speed</span>
                                      <span className="font-mono">{profiles[m.id]?.speed || "—"}</span>
                                    </div>
                                    <div>
                                      <span className="mr-1">Quality</span>
                                      <span className="font-mono">{profiles[m.id]?.quality || "—"}</span>
                                    </div>
                                    <div>
                                      <span className="mr-1">Cost</span>
                                      <span className="font-mono">{profiles[m.id]?.cost || "—"}</span>
                                    </div>
                                  </div>
                                </div>
                              </SelectItem>
                            );
                          })
                        )}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm">Language</label>
                    <Input
                      placeholder="e.g., python, javascript, rust..."
                      className="font-mono text-sm"
                      value={language}
                      onChange={(e) => setLanguage(e.target.value.toLowerCase())}
                    />
                  </div>
                </div>

                <Button
                  className="w-full"
                  onClick={handleGenerate}
                  disabled={isGenerating || !prompt.trim()}
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-4 w-4" />
                      Generate Code
                    </>
                  )}
                </Button>

                <div className="space-y-2 border-t pt-4">
                  <div className="text-sm text-muted-foreground">
                    Example prompts:
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {examples.map((example, i) => (
                      <Badge
                        key={i}
                        variant="secondary"
                        className="cursor-pointer text-xs"
                        onClick={() => setPrompt(example)}
                      >
                        {example}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Output Panel */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Code2 className="h-5 w-5" />
                    Generated Output
                  </CardTitle>
                  <div className="flex gap-2">
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={handleCopy}
                      aria-label={copied ? "Copied" : "Copy code"}
                    >
                      {copied ? (
                        <Check className="h-4 w-4" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      aria-label="Download code"
                      onClick={() => {
                        const fallback = exampleCode[language as keyof typeof exampleCode] || exampleCode.python;
                        const code = generatedCode || fallback;
                        const blob = new Blob([code], { type: "text/plain;charset=utf-8" });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        const ext = language === "python" ? "py" : language === "javascript" ? "js" : language === "sql" ? "sql" : "txt";
                        a.href = url;
                        a.download = `generated.${ext}`;
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                        URL.revokeObjectURL(url);
                      }}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {errorMessage && (
                  <Alert variant="destructive" className="mb-3">
                    <AlertTitle>Generation Error</AlertTitle>
                    <AlertDescription>{errorMessage}</AlertDescription>
                  </Alert>
                )}
                <Tabs defaultValue="code" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="code">Code</TabsTrigger>
                    <TabsTrigger value="info">Info</TabsTrigger>
                  </TabsList>
                  <TabsContent value="code" className="mt-4">
                    <div className="h-[400px] overflow-auto rounded-md border bg-muted/30">
                      <pre className="p-4 text-xs font-mono">
                        <code
                          ref={codeRef as any}
                          className={`language-${(language || "").toLowerCase()}`}
                        >
                          {displayCode}
                        </code>
                      </pre>
                    </div>
                  </TabsContent>
                  <TabsContent value="info" className="mt-4">
                    <div className="h-[400px] overflow-auto">
                      <div className="space-y-4 text-sm">
                        <div>
                          <h4 className="mb-2">Model Information</h4>
                          <div className="rounded-md border bg-muted/30 p-3 font-mono text-xs">
                            <div>Model: {model === "openai" ? "gpt-3.5-turbo" : model}</div>
                            <div>Language: {language || "auto-detect"}</div>
                            <div>Generated: Just now</div>
                            <div className="mt-2 grid grid-cols-3 gap-2 text-[11px]">
                              <div>
                                <span className="text-muted-foreground">Speed</span>
                                <div>{profiles[model]?.speed || "—"}</div>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Quality</span>
                                <div>{profiles[model]?.quality || "—"}</div>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Cost</span>
                                <div>{profiles[model]?.cost || "—"}</div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <SessionAnalytics refreshKey={`${generatedCode}:${errorMessage}:${model}`} />
                        <div>
                          <h4 className="mb-2">Features</h4>
                          <ul className="space-y-1 text-muted-foreground">
                            <li>• Syntax highlighting with Prism.js</li>
                            <li>• Language auto-detection</li>
                            <li>• Export to file or clipboard</li>
                            <li>• Error handling included</li>
                          </ul>
                        </div>
                        <div>
                          <h4 className="mb-2">Usage</h4>
                          <p className="text-muted-foreground">
                            Copy the generated code and integrate it into your project. 
                            Review and test before production use.
                          </p>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}
