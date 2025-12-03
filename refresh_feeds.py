from __future__ import annotations

import json
from feeds.aggregator import aggregate_all


def main() -> int:
    data = aggregate_all()
    # Print minimal status for cron logs
    print(json.dumps({"updated": data.get("updated"), "count": len(data.get("items", []))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


