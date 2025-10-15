import { ArrowRight } from "lucide-react";
import { Card } from "./ui/card";

export function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Input Validation",
      description: "Sanitizes and validates user prompts for security",
    },
    {
      number: "02",
      title: "Model Routing",
      description: "Routes request to selected AI model (OpenAI/HF/Local)",
    },
    {
      number: "03",
      title: "Prompt Engineering",
      description: "Optimizes prompts for accurate code generation",
    },
    {
      number: "04",
      title: "AI Processing",
      description: "Generates code using advanced language models",
    },
    {
      number: "05",
      title: "Code Extraction",
      description: "Extracts and cleans generated code from response",
    },
    {
      number: "06",
      title: "Syntax Highlighting",
      description: "Applies Prism.js highlighting for readability",
    },
  ];

  return (
    <section className="border-b py-16 md:py-20">
      <div className="container px-4 md:px-6">
        <div className="mb-12 text-center">
          <h2 className="mb-3">How It Works</h2>
          <p className="text-muted-foreground">
            A streamlined pipeline from natural language to production code
          </p>
        </div>

        <div className="mx-auto max-w-5xl">
          {/* Flow Diagram */}
          <div className="mb-8 rounded-lg border bg-muted/30 p-6">
            <div className="flex items-center justify-between overflow-x-auto pb-2">
              <div className="flex items-center gap-3 text-sm font-mono">
                <span className="whitespace-nowrap text-muted-foreground">Prompt</span>
                <ArrowRight className="h-4 w-4 text-primary" />
                <span className="whitespace-nowrap text-muted-foreground">Model</span>
                <ArrowRight className="h-4 w-4 text-primary" />
                <span className="whitespace-nowrap text-muted-foreground">AI</span>
                <ArrowRight className="h-4 w-4 text-primary" />
                <span className="whitespace-nowrap text-muted-foreground">Extract</span>
                <ArrowRight className="h-4 w-4 text-primary" />
                <span className="whitespace-nowrap text-muted-foreground">Highlight</span>
                <ArrowRight className="h-4 w-4 text-primary" />
                <span className="whitespace-nowrap text-primary">Code</span>
              </div>
            </div>
          </div>

          {/* Process Steps */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {steps.map((step, index) => (
              <Card key={index} className="p-4 transition-shadow hover:shadow-md">
                <div className="mb-2 font-mono text-2xl text-primary/40">
                  {step.number}
                </div>
                <h4 className="mb-1">{step.title}</h4>
                <p className="text-sm text-muted-foreground">
                  {step.description}
                </p>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
