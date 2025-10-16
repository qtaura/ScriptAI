import { Button } from "./ui/button";
import { ArrowRight, Terminal, Github } from "lucide-react";
import { Badge } from "./ui/badge";

export function Hero() {
  return (
    <section className="relative overflow-hidden border-b">
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-background to-background" />
      
      <div className="container relative px-4 py-16 md:px-6 md:py-24">
        <div className="mx-auto max-w-3xl text-center">
          <Badge variant="secondary" className="mb-4 font-mono">
            v1.4.0
          </Badge>
          
          <h1 className="mb-4 text-3xl md:text-5xl leading-tight text-pretty">
            Natural Language →{" "}
            <span className="text-primary">Production Code</span>
          </h1>
          
          <p className="mb-8 text-lg leading-relaxed text-muted-foreground text-pretty">
            AI-powered code generation platform with multi-model support. Transform requirements into 
            production-ready scripts across 50+ languages.
          </p>
          
          <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button size="lg" asChild className="w-full sm:w-auto">
              <a href="#generator">
                Try Generator
                <ArrowRight className="ml-2 h-4 w-4" />
              </a>
            </Button>
            <Button size="lg" variant="outline" asChild className="w-full sm:w-auto">
              <a
                href="https://github.com/qtaura/ScriptAI"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Github className="mr-2 h-4 w-4" />
                View on GitHub
              </a>
            </Button>
          </div>

          {/* Code Preview */}
          <div className="mt-12 rounded-lg border bg-card p-4 text-left shadow-lg">
            <div className="mb-3 flex items-center gap-2 border-b pb-2">
              <Terminal className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-mono text-muted-foreground">Quick Start</span>
            </div>
            <div className="space-y-1 font-mono text-sm">
              <div className="text-muted-foreground">
                <span className="text-primary">$</span> pip install -r requirements.txt
              </div>
              <div className="text-muted-foreground">
                <span className="text-primary">$</span> python app.py
              </div>
              <div className="text-green-600">
                ✓ ScriptAI running on http://127.0.0.1:5000/
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
