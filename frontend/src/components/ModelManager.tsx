import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Switch } from "./ui/switch";
import { Separator } from "./ui/separator";

type ModelInfo = { id: string; name: string; speed?: string; quality?: string; cost?: string };

export function ModelManager() {
  const [available, setAvailable] = useState<string[]>([]);
  const [disabled, setDisabled] = useState<string[]>([]);
  const [allModels, setAllModels] = useState<ModelInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Load static model cards for names and attributes
  useEffect(() => {
    fetch("/modelCards.json")
      .then((r) => r.json())
      .then((data) => {
        const arr = Array.isArray(data?.models) ? data.models : [];
        setAllModels(arr.map((m: any) => ({ id: String(m.id), name: String(m.name), speed: m.speed, quality: m.quality, cost: m.cost })));
      })
      .catch(() => {
        setAllModels([
          { id: "openai", name: "OpenAI GPT-3.5" },
          { id: "anthropic", name: "Anthropic Claude" },
          { id: "gemini", name: "Google Gemini" },
          { id: "huggingface", name: "HuggingFace StarCoder" },
          { id: "local", name: "Local Model" },
        ]);
      });
  }, []);

  // Load available models from backend
  useEffect(() => {
    setError(null);
    fetch("/models")
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      })
      .then((data) => {
        const ids = Array.isArray(data) ? data.map(String) : [];
        setAvailable(ids);
      })
      .catch((e) => {
        setError(`Failed to load models (${e?.message ?? "unknown"}). Using fallback.`);
        // Fallback: assume static IDs from model cards
        setAvailable((prev) => (prev.length ? prev : allModels.map((m) => m.id)));
      });
  }, [allModels.length]);

  // Sync disabled state from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem("scriptai.disabled_models");
      const arr = raw ? JSON.parse(raw) : [];
      setDisabled(Array.isArray(arr) ? arr.map(String) : []);
    } catch {}
  }, []);

  const list = useMemo(() => {
    // Merge cards with availability
    const ids = new Set(available);
    return allModels.map((m) => ({ ...m, available: ids.has(m.id) }));
  }, [allModels, available]);

  const toggle = (id: string, next: boolean) => {
    setDisabled((prev) => {
      const arr = next ? Array.from(new Set([...prev, id])) : prev.filter((x) => x !== id);
      try {
        localStorage.setItem("scriptai.disabled_models", JSON.stringify(arr));
      } catch {}
      // Inform other components (e.g., CodeGenerator) that availability changed
      try {
        window.dispatchEvent(new Event("scriptai:models-updated"));
      } catch {}
      return arr;
    });
  };

  return (
    <section id="models" className="border-b py-16 md:py-20">
      <div className="container px-4 md:px-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Model Manager</h2>
            <p className="text-muted-foreground">Enable or disable providers locally</p>
          </div>
          <Badge variant="default">Local Only</Badge>
        </div>

        {error && (
          <div className="mb-4 text-sm text-destructive">{error}</div>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Providers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {list.map((m) => {
                const isDisabled = disabled.includes(m.id);
                return (
                  <div key={m.id} className="flex items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{m.name}</span>
                        {!m.available && (
                          <Badge variant="secondary">requires key</Badge>
                        )}
                        {isDisabled && (
                          <Badge variant="destructive">disabled</Badge>
                        )}
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground grid grid-cols-3 gap-2">
                        <span>Speed: {m.speed ?? "—"}</span>
                        <span>Quality: {m.quality ?? "—"}</span>
                        <span>Cost: {m.cost ?? "—"}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-muted-foreground">Disable</span>
                      <Switch
                        checked={isDisabled}
                        onCheckedChange={(checked: boolean) => toggle(m.id, checked)}
                        aria-label={`Disable ${m.name}`}
                      />
                    </div>
                  </div>
                );
              })}
              {list.length === 0 && (
                <div className="text-sm text-muted-foreground">No providers loaded</div>
              )}
            </div>
            <Separator className="my-4" />
            <p className="text-xs text-muted-foreground">
              Tip: This setting is stored in your browser and only affects your local session.
            </p>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}