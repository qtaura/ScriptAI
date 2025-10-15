import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Check } from "lucide-react";
import { getIcon } from "../config/iconMap";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";

type ModelCardConfig = {
  id?: string;
  name: string;
  badge: string;
  speed: string;
  quality: string;
  cost: string;
  icon?: string;
  features: string[];
  color: string;
  bgColor: string;
};

export function ModelComparison() {
  const [models, setModels] = useState<ModelCardConfig[]>([]);
  const [configError, setConfigError] = useState<string>("");

  useEffect(() => {
    // Prefer backend dynamic profiles; fallback to public/modelCards.json
    fetch("/model-profiles")
      .then((r) => r.json())
      .then((data: { models?: any[] }) => {
        const items = Array.isArray(data?.models) ? data!.models! : [];
        const valid = items
          .map((m) => ({
            id: m?.id,
            name: String(m?.name || ""),
            badge: String(m?.badge || ""),
            speed: String(m?.speed || ""),
            quality: String(m?.quality || ""),
            cost: String(m?.cost || ""),
            icon: String(m?.icon || ""),
            features: Array.isArray(m?.features) ? m.features : [],
            color: "text-green-600",
            bgColor: "bg-green-600/10",
          }))
          .filter(
            (m) =>
              m && m.name && m.badge && m.speed && m.quality && m.cost && Array.isArray(m.features),
          );
        if (valid.length === 0) throw new Error("Invalid backend profiles");
        setModels(valid);
      })
      .catch(() => {
        // Fallback to public config or SPA-served path when Flask serves UI from /ui/*
        fetch("/modelCards.json")
          .then((r) => r.json())
          .then((data: { models?: ModelCardConfig[] }) => {
            const items = (data && data.models) || [];
            if (items.length === 0) {
              setConfigError("No model cards found in configuration. Showing defaults.");
              setModels(defaultModels);
              return;
            }
            const valid = items.filter(
              (m) =>
                m && typeof m.name === "string" && m.name && typeof m.badge === "string" && m.badge &&
                typeof m.speed === "string" && typeof m.quality === "string" && typeof m.cost === "string" &&
                Array.isArray(m.features),
            );
            if (valid.length < items.length) {
              setConfigError("Some model entries in configuration are invalid. Rendering available items.");
            }
            if (valid.length === 0) {
              setConfigError("Failed to parse model cards configuration. Showing defaults.");
              setModels(defaultModels);
              return;
            }
            setModels(valid);
          })
          .catch(() => {
            fetch("/ui/modelCards.json")
              .then((r) => r.json())
              .then((data: { models?: ModelCardConfig[] }) => {
                const items = (data && data.models) || [];
                const valid = items.filter(
                  (m) =>
                    m && typeof m.name === "string" && m.name && typeof m.badge === "string" && m.badge &&
                    typeof m.speed === "string" && typeof m.quality === "string" && typeof m.cost === "string" &&
                    Array.isArray(m.features),
                );
                if (valid.length === 0) {
                  setConfigError("Unable to load model cards configuration. Showing defaults.");
                  setModels(defaultModels);
                  return;
                }
                setModels(valid);
              })
              .catch(() => {
                setConfigError("Unable to load model cards configuration. Showing defaults.");
                setModels(defaultModels);
              });
          });
      });
  }, []);

  const defaultModels: ModelCardConfig[] = [
    {
      id: "openai",
      name: "OpenAI GPT-3.5",
      badge: "Recommended",
      speed: "Fast",
      quality: "High",
      cost: "Paid",
      icon: "Zap",
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
      id: "anthropic",
      name: "Anthropic Claude",
      badge: "Reliable",
      speed: "Fast",
      quality: "High",
      cost: "Paid",
      icon: "Sparkles",
      features: [
        "Strong reasoning",
        "Safe outputs",
        "Long context windows",
        "Great coding assistance",
      ],
      color: "text-amber-600",
      bgColor: "bg-amber-600/10",
    },
    {
      id: "gemini",
      name: "Google Gemini",
      badge: "Powerful",
      speed: "Fast",
      quality: "High",
      cost: "Paid",
      icon: "Brain",
      features: [
        "Multi-modal capabilities",
        "Strong reasoning",
        "Good code generation",
        "Google ecosystem integration",
      ],
      color: "text-teal-600",
      bgColor: "bg-teal-600/10",
    },
    {
      id: "huggingface",
      name: "HuggingFace StarCoder",
      badge: "Open Source",
      speed: "Medium",
      quality: "Good",
      cost: "Free",
      icon: "Clock",
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
      id: "local",
      name: "Local Model",
      badge: "Privacy",
      speed: "Slow",
      quality: "Variable",
      cost: "Free",
      icon: "DollarSign",
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
          {configError && (
            <div className="md:col-span-3">
              <Alert variant="destructive">
                <AlertTitle>Model Cards Error</AlertTitle>
                <AlertDescription>{configError}</AlertDescription>
              </Alert>
            </div>
          )}
          {models.map((model, index) => {
            const Icon = getIcon(model.icon);
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
