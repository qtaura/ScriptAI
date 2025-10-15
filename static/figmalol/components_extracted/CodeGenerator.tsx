import { useState } from "react";
import { Button } from "./ui/button";
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

export function CodeGenerator() {
  const [prompt, setPrompt] = useState("");
  const [model, setModel] = useState("openai");
  const [language, setLanguage] = useState("python");
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

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

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
    }, 1500);
  };

  const handleCopy = () => {
    const code = exampleCode[language as keyof typeof exampleCode] || exampleCode.python;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const displayCode = exampleCode[language as keyof typeof exampleCode] || exampleCode.python;

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
                  <div className="space-y-2">
                    <label className="text-sm">AI Model</label>
                    <Select value={model} onValueChange={setModel}>
                      <SelectTrigger className="font-mono">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="openai">OpenAI GPT-3.5</SelectItem>
                        <SelectItem value="huggingface">HuggingFace</SelectItem>
                        <SelectItem value="local">Local Model</SelectItem>
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
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="code" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="code">Code</TabsTrigger>
                    <TabsTrigger value="info">Info</TabsTrigger>
                  </TabsList>
                  <TabsContent value="code" className="mt-4">
                    <div className="h-[400px] overflow-auto rounded-md border bg-muted/30">
                      <pre className="p-4 text-xs font-mono">
                        <code>{displayCode}</code>
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
                          </div>
                        </div>
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
