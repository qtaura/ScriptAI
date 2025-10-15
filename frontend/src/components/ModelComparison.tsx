import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Check, Zap, Clock, DollarSign } from "lucide-react";

export function ModelComparison() {
  const models = [
    {
      name: "OpenAI GPT-3.5",
      badge: "Recommended",
      speed: "Fast",
      quality: "High",
      cost: "Paid",
      icon: Zap,
      features: [
        "Production-ready code",
        "Complex algorithms",
        "Best error handling",
        "Extensive language support",
      ],
      color: "text-green-600",
      bgColor: "bg-green-600/10",
    },
    {
      name: "HuggingFace StarCoder",
      badge: "Open Source",
      speed: "Medium",
      quality: "Good",
      cost: "Free",
      icon: Clock,
      features: [
        "Code completion",
        "Good for snippets",
        "Open source models",
        "No API costs",
      ],
      color: "text-blue-600",
      bgColor: "bg-blue-600/10",
    },
    {
      name: "Local Model",
      badge: "Privacy",
      speed: "Slow",
      quality: "Variable",
      cost: "Free",
      icon: DollarSign,
      features: [
        "Offline capability",
        "Complete privacy",
        "No API dependencies",
        "Customizable",
      ],
      color: "text-purple-600",
      bgColor: "bg-purple-600/10",
    },
  ];

  return (
    <section id="models" className="border-b py-16 md:py-20">
      <div className="container px-4 md:px-6">
        <div className="mb-12 text-center">
          <h2 className="mb-3">Multi-Model Support</h2>
          <p className="text-muted-foreground">
            Choose between commercial APIs or run models locally
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {models.map((model, index) => {
            const Icon = model.icon;
            return (
              <Card key={index} className="relative overflow-hidden transition-shadow hover:shadow-md">
                <div className={`absolute top-0 right-0 h-24 w-24 ${model.bgColor} blur-3xl`} />
                <CardHeader>
                  <div className="mb-2">
                    <Badge variant="secondary" className="mb-2">
                      {model.badge}
                    </Badge>
                  </div>
                  <CardTitle className="flex items-center gap-2">
                    <Icon className={`h-5 w-5 ${model.color}`} />
                    {model.name}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <div>
                      <div className="text-muted-foreground">Speed</div>
                      <div className="font-mono">{model.speed}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Quality</div>
                      <div className="font-mono">{model.quality}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Cost</div>
                      <div className="font-mono">{model.cost}</div>
                    </div>
                  </div>
                  <div className="space-y-2 pt-2">
                    {model.features.map((feature, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}
