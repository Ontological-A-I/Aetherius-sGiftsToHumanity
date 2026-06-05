# ===== FILE: services/tool_meta_optimizer.py =====
import os
import json
import datetime


class ToolMetaOptimizer:
    def __init__(self, data_directory="/data/Memories/"):
        self.data_directory = data_directory
        self.log_dir = os.path.join(self.data_directory, "ToolUsage")
        self.log_file = os.path.join(self.log_dir, "tool_usage_log.jsonl")
        self.report_file = os.path.join(self.log_dir, "optimization_report.jsonl")
        os.makedirs(self.log_dir, exist_ok=True)
        print("[ToolMetaOptimizer] Usage logging layer online.", flush=True)

    def log_invocation(self, tool_name: str, args_summary: dict, outcome: str,
                       duration_ms: float, success: bool):
        """Appends one atomic JSONL transaction line per tool call."""
        # Sanitize args — strip large content blobs to keep log scannable
        safe_args = {}
        for k, v in (args_summary or {}).items():
            sv = str(v)
            safe_args[k] = sv[:200] + "…" if len(sv) > 200 else sv

        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "tool_name": tool_name,
            "arguments": safe_args,
            "duration_ms": round(duration_ms, 2),
            "success": success,
            "outcome_summary": str(outcome)[:500],
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"[ToolMetaOptimizer] WARNING: Could not write log entry: {e}", flush=True)

    def analyze_tool_patterns(self) -> dict:
        """Reads the full usage log and returns a structured efficiency matrix."""
        if not os.path.exists(self.log_file):
            return {"status": "No usage log exists yet. Tools have not been called."}

        usage_counts: dict = {}
        failure_counts: dict = {}
        durations: dict = {}
        last_used: dict = {}

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    name = entry.get("tool_name", "unknown")
                    usage_counts[name] = usage_counts.get(name, 0) + 1
                    if not entry.get("success", True):
                        failure_counts[name] = failure_counts.get(name, 0) + 1
                    durations.setdefault(name, []).append(entry.get("duration_ms", 0))
                    ts = entry.get("timestamp", "")
                    if ts > last_used.get(name, ""):
                        last_used[name] = ts

            analytics = []
            for name, count in sorted(usage_counts.items(),
                                      key=lambda x: x[1], reverse=True):
                fails = failure_counts.get(name, 0)
                avg_ms = sum(durations[name]) / len(durations[name])
                analytics.append({
                    "tool_name": name,
                    "total_invocations": count,
                    "failure_count": fails,
                    "failure_rate": round(fails / count, 4),
                    "average_latency_ms": round(avg_ms, 2),
                    "last_used": last_used.get(name, ""),
                })

            report = {
                "report_timestamp": datetime.datetime.utcnow().isoformat(),
                "total_tools_tracked": len(analytics),
                "metrics_summary": analytics,
            }
            with open(self.report_file, "a", encoding="utf-8") as rf:
                rf.write(json.dumps(report) + "\n")
            return report

        except Exception as e:
            return {"error": f"Pattern analysis failed: {e}"}
