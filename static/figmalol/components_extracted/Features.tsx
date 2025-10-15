import {
  Shield,
  Activity,
  Gauge,
  Lock,
  FileCode,
  Laptop,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

export function Features() {
  const features = [
    {
      icon: Shield,
      title: "Security First",
      description:
        "Input validation, XSS protection, and rate limiting (100/hour per IP) built-in.",
    },
    {
      icon: Activity,
      title: "Production Monitoring",
      description:
        "Prometheus metrics, health checks, and performance tracking at /metrics endpoint.",
    },
    {
      icon: Gauge,
      title: "Rate Limiting",
      description:
        "Flask-Limiter enforces per-IP limits with 429 responses to prevent abuse.",
    },
    {
      icon: Lock,
      title: "Input Sanitization",
      description:
        "Automatic HTML escaping and malicious pattern detection for all user inputs.",
    },
    {
      icon: FileCode,
      title: "50+ Languages",
      description:
        "Generate code in Python, JavaScript, SQL, Bash, Rust, Go, and 45+ more languages.",
    },
    {
      icon: Laptop,
      title: "Dual Interface",
      description:
        "Choose between intuitive web UI or powerful CLI for your workflow preferences.",
    },
  ];

  return (
    <section id="features" className="border-b py-16 md:py-20">
      <div className="container px-4 md:px-6">
        <div className="mb-12 text-center">
          <h2 className="mb-3">Core Features</h2>
          <p className="text-muted-foreground">
            Security, monitoring, and multi-language support built-in
          </p>
        </div>

        <div className="mx-auto max-w-5xl">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card key={index} className="transition-shadow hover:shadow-md">
                  <CardHeader>
                    <div className="mb-2 inline-flex h-10 w-10 items-center justify-center rounded-md bg-primary/10">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                    <CardTitle>{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Additional Info */}
          <div className="mt-8 rounded-lg border bg-muted/30 p-6">
            <h4 className="mb-4">Monitoring Endpoints</h4>
            <div className="grid gap-2 font-mono text-sm md:grid-cols-2">
              <div className="flex items-center gap-2">
                <span className="text-primary">/health</span>
                <span className="text-muted-foreground">System health check</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-primary">/stats</span>
                <span className="text-muted-foreground">Usage statistics</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-primary">/metrics</span>
                <span className="text-muted-foreground">Prometheus metrics</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-primary">/performance</span>
                <span className="text-muted-foreground">Performance data</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
