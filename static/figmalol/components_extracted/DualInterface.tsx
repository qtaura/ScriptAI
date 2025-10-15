import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Terminal, Globe } from "lucide-react";
import { Badge } from "./ui/badge";

export function DualInterface() {
  return (
    <section className="border-b py-16 md:py-20">
      <div className="container px-4 md:px-6">
        <div className="mb-12 text-center">
          <h2 className="mb-3">Two Interfaces</h2>
          <p className="text-muted-foreground">
            Use the web UI for visual editing or CLI for automation
          </p>
        </div>

        <div className="mx-auto max-w-4xl">
          <Tabs defaultValue="web" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="web" className="gap-2">
                <Globe className="h-4 w-4" />
                Web Interface
              </TabsTrigger>
              <TabsTrigger value="cli" className="gap-2">
                <Terminal className="h-4 w-4" />
                CLI
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="web" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Globe className="h-5 w-5" />
                    Web Interface
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="rounded-md border bg-muted/30 p-4 font-mono text-sm">
                    <div className="text-muted-foreground">
                      <span className="text-primary">$</span> python app.py
                    </div>
                    <div className="text-green-600">
                      ✓ Running on http://127.0.0.1:5000/
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h4>Features:</h4>
                    <ul className="grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Visual code editor</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Syntax highlighting</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Model selection</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Copy/download</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Real-time generation</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Responsive design</span>
                      </li>
                    </ul>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary">Flask Backend</Badge>
                    <Badge variant="secondary">Prism.js Highlighting</Badge>
                    <Badge variant="secondary">REST API</Badge>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="cli" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Terminal className="h-5 w-5" />
                    Command Line Interface
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="text-sm">Interactive Mode:</div>
                    <div className="rounded-md border bg-muted/30 p-4 font-mono text-sm">
                      <div className="text-muted-foreground">
                        <span className="text-primary">$</span> python cli.py -i
                      </div>
                      <div className="text-green-600">
                        ✓ Interactive mode enabled
                      </div>
                      <div className="text-muted-foreground">
                        <span className="text-primary">&gt;</span> model openai
                      </div>
                      <div className="text-muted-foreground">
                        <span className="text-primary">&gt;</span> Create a quicksort function
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm">Direct Command:</div>
                    <div className="rounded-md border bg-muted/30 p-4 font-mono text-sm">
                      <div className="text-muted-foreground">
                        <span className="text-primary">$</span> python cli.py "Create quicksort" \
                      </div>
                      <div className="text-muted-foreground pl-4">
                        --model openai --file sort.py
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <h4>Features:</h4>
                    <ul className="grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Interactive sessions</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Context preservation</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Direct file output</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Model switching</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Batch processing</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span>•</span>
                        <span>Scriptable automation</span>
                      </li>
                    </ul>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary">Python CLI</Badge>
                    <Badge variant="secondary">Stateful Sessions</Badge>
                    <Badge variant="secondary">File Export</Badge>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </section>
  );
}
