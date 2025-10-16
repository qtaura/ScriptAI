import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Separator } from "./ui/separator";

type MetricsJson = {
  usage: {
    total_requests?: number;
    total_tokens?: number;
    by_model?: Record<string, { requests: number; tokens?: number }>;
  };
  performance: {
    avg_latency_ms?: number;
    p95_latency_ms?: number;
    last_minute_rps?: number;
  };
  health: {
    ok: boolean;
    details?: Record<string, boolean | string>;
  };
};

type SecurityStats = {
  rate_limit_hits?: number;
  blocked_requests?: number;
  sanitized_inputs?: number;
  last_blocked_ip?: string | null;
};

export function MetricsPanel() {
  const [metrics, setMetrics] = useState<MetricsJson | null>(null);
  const [security, setSecurity] = useState<SecurityStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchAll = async () => {
    try {
      setError(null);
      const [mRes, sRes] = await Promise.all([
        fetch("/metrics-json"),
        fetch("/security-stats"),
      ]);
      if (!mRes.ok) throw new Error(`metrics-json ${mRes.status}`);
      if (!sRes.ok) throw new Error(`security-stats ${sRes.status}`);
      const m = (await mRes.json()) as MetricsJson;
      const s = (await sRes.json()) as SecurityStats;
      setMetrics(m);
      setSecurity(s);
    } catch (e: any) {
      setError(e?.message ?? "Failed to fetch metrics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, 15000);
    return () => clearInterval(id);
  }, []);

  const healthOk = metrics?.health?.ok ?? false;
  const totalReq = metrics?.usage?.total_requests ?? 0;
  const avgLatency = metrics?.performance?.avg_latency_ms ?? 0;
  const p95Latency = metrics?.performance?.p95_latency_ms ?? 0;
  const rps = metrics?.performance?.last_minute_rps ?? 0;

  const modelBreakdown = useMemo(() => {
    const byModel = metrics?.usage?.by_model ?? {};
    const sum = Object.values(byModel).reduce((acc, v) => acc + (v?.requests ?? 0), 0);
    return { byModel, sum };
  }, [metrics]);

  return (
    <section id="metrics" className="py-16">
      <div className="container px-4 md:px-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">System Metrics</h2>
            <p className="text-muted-foreground">Live usage, performance, and security signals</p>
          </div>
          <Badge variant={healthOk ? "default" : "destructive"}>
            {healthOk ? "Healthy" : "Degraded"}
          </Badge>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Overview</CardTitle>
            <CardDescription>Auto-refreshes every 15 seconds</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-sm text-muted-foreground">Loading metrics…</p>
            ) : error ? (
              <p className="text-sm text-destructive">{error}</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <div className="text-sm text-muted-foreground">Requests (24h)</div>
                  <div className="text-2xl font-semibold">{totalReq.toLocaleString()}</div>
                  <Separator className="my-3" />
                  <div className="space-y-2">
                    {Object.entries(modelBreakdown.byModel).map(([model, v]) => {
                      const pct = modelBreakdown.sum
                        ? Math.round(((v?.requests ?? 0) / modelBreakdown.sum) * 100)
                        : 0;
                      return (
                        <div key={model}>
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-muted-foreground">{model}</span>
                            <span>{v.requests.toLocaleString()} • {pct}%</span>
                          </div>
                          <Progress value={pct} />
                        </div>
                      );
                    })}
                    {Object.keys(modelBreakdown.byModel).length === 0 && (
                      <div className="text-sm text-muted-foreground">No model usage yet</div>
                    )}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Performance</div>
                  <div className="mt-2 grid grid-cols-2 gap-3">
                    <div>
                      <div className="text-xs text-muted-foreground">Avg Latency</div>
                      <div className="text-xl font-medium">{Math.round(avgLatency)} ms</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">p95 Latency</div>
                      <div className="text-xl font-medium">{Math.round(p95Latency)} ms</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Last-minute RPS</div>
                      <div className="text-xl font-medium">{rps.toFixed(2)}</div>
                    </div>
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Security</div>
                  <div className="mt-2 grid grid-cols-2 gap-3">
                    <div>
                      <div className="text-xs text-muted-foreground">Rate limit hits</div>
                      <div className="text-xl font-medium">{security?.rate_limit_hits ?? 0}</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Blocked requests</div>
                      <div className="text-xl font-medium">{security?.blocked_requests ?? 0}</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Sanitized inputs</div>
                      <div className="text-xl font-medium">{security?.sanitized_inputs ?? 0}</div>
                    </div>
                    {security?.last_blocked_ip && (
                      <div className="col-span-2">
                        <div className="text-xs text-muted-foreground">Last blocked IP</div>
                        <div className="text-sm font-mono">{security.last_blocked_ip}</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Tabs defaultValue="raw" className="mt-6">
          <TabsList>
            <TabsTrigger value="raw">Raw Metrics</TabsTrigger>
            <TabsTrigger value="health">Health Details</TabsTrigger>
          </TabsList>
          <TabsContent value="raw">
            <pre className="mt-3 rounded-md bg-muted p-4 text-xs overflow-auto">
{JSON.stringify(metrics ?? {}, null, 2)}
            </pre>
          </TabsContent>
          <TabsContent value="health">
            <pre className="mt-3 rounded-md bg-muted p-4 text-xs overflow-auto">
{JSON.stringify(metrics?.health ?? {}, null, 2)}
            </pre>
          </TabsContent>
        </Tabs>
      </div>
    </section>
  );
}