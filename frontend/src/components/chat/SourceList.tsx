import type { SourceReference } from "@/lib/api/types";

interface SourceListProps {
  sources: SourceReference[];
}

export function SourceList({ sources }: SourceListProps) {
  if (sources.length === 0) return null;

  return (
    <div className="border-border bg-muted/40 mt-3 rounded-lg border p-3">
      <p className="text-muted-foreground mb-2 text-xs font-medium uppercase tracking-wide">
        Sources
      </p>
      <ul className="flex flex-col gap-2">
        {sources.map((source) => (
          <li
            key={source.doc_id}
            className="border-border bg-background rounded-md border p-2.5 text-sm"
          >
            <div className="mb-1 flex items-center justify-between gap-2">
              <span className="font-medium">{source.source_file}</span>
              <span className="text-muted-foreground text-xs">
                {(source.score * 100).toFixed(0)}% match
              </span>
            </div>
            <p className="text-muted-foreground line-clamp-3 text-xs leading-relaxed">
              {source.snippet}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
