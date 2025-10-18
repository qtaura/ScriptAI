import { useEffect, useState } from "react";

type Analytics = {
  messages_count: number;
  tokens_estimated: number;
  models_used: Record<string, number>;
  primary_model: string | null;
  consistent: boolean;
  context_key?: string;
};

export function SessionAnalytics({ refreshKey }: { refreshKey?: string }) {
  const [data, setData] = useState<Analytics | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/session-analytics");
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(body?.error || `Failed to load analytics (${res.status})`);
        setData(null);
      } else {
        const d: Analytics = {
          messages_count: Number(body?.messages_count || 0),
          tokens_estimated: Number(body?.tokens_estimated || 0),
          models_used: (body?.models_used && typeof body.models_used === "object") ? body.models_used : {},
          primary_model: (typeof body?.primary_model === "string") ? body.primary_model : null,
          consistent: Boolean(body?.consistent),
          context_key: typeof body?.context_key === "string" ? body.context_key : undefined,
        };
        setData(d);
      }
    } catch (e: any) {
      setError(e?.message || "Network error");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey]);

  return (
    <div>
      <h4 className="mb-2">Session Analytics</h4>
      {error && (
        <div className="rounded-md border bg-red-50 p-3 text-xs text-red-900">
          {error}
        </div>
      )}
      {!error && (
        <div className="rounded-md border bg-muted/30 p-3 text-xs font-mono">
          <div className="grid grid-cols-3 gap-3">
            <div>
              <div className="text-muted-foreground">Messages</div>
              <div className="text-sm">{data?.messages_count ?? 0}</div>
            </div>
            <div>
              <div className="text-muted-foreground">Tokens (est.)</div>
              <div className="text-sm">{data?.tokens_estimated ?? 0}</div>
            </div>
            <div>
              <div className="text-muted-foreground">Model Consistency</div>
              <div className="text-sm">{(data?.consistent ? "Consistent" : "Switched")}</div>
            </div>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <div>
              <div className="text-muted-foreground">Primary Model</div>
              <div className="text-sm">{data?.primary_model || "—"}</div>
            </div>
            <div>
              <div className="text-muted-foreground">Models Used</div>
              <div className="text-xs">
                {data && data.models_used && Object.keys(data.models_used).length > 0 ? (
                  Object.entries(data.models_used)
                    .sort((a, b) => b[1] - a[1])
                    .map(([m, c]) => (
                      <span key={m} className="mr-2">
                        {m}:{c}
                      </span>
                    ))
                ) : (
                  <span>—</span>
                )}
              </div>
            </div>
          </div>
          {loading && (
            <div className="mt-2 text-[11px] text-muted-foreground">Loading…</div>
          )}
        </div>
      )}
    </div>
  );
}