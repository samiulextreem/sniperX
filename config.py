import json
import os
from typing import Dict, Any, List


DEFAULT_CONFIG = {
	"token_ids": [
		"90044929278592762736809672799012603596750177679616629362026647999260321317755"
	],
	"investment": 0,
	"min_value": 20.0
}


def _normalize_tokens(conf: Dict[str, Any]) -> List[Dict[str, str]]:
	"""Return a normalized list of tokens as [{id, slug?}]."""
	# New format: tokens: [{"id": "...", "slug": "..."}]
	tokens = conf.get("tokens")
	if isinstance(tokens, list) and tokens:
		normalized = []
		for t in tokens:
			if isinstance(t, dict) and "id" in t:
				item = {"id": str(t["id"])}
				if "slug" in t and t["slug"]:
					item["slug"] = str(t["slug"])
				normalized.append(item)
		return normalized
	# Back-compat: token_ids: ["..."]
	token_ids = conf.get("token_ids")
	if isinstance(token_ids, list) and token_ids:
		return [{"id": str(tid)} for tid in token_ids]
	# Fallback to defaults
	return [{"id": tid} for tid in DEFAULT_CONFIG["token_ids"]]


def load_config(path: str = "config.json") -> Dict[str, Any]:
	"""Load configuration from JSON file, falling back to defaults.
	Returns a dict with 'tokens' (list of {id, slug?}), 'investment', 'min_value'.
	"""
	if not os.path.exists(path):
		return {
			"tokens": _normalize_tokens(DEFAULT_CONFIG),
			"investment": DEFAULT_CONFIG["investment"],
			"min_value": DEFAULT_CONFIG["min_value"],
		}
	try:
		with open(path, 'r') as f:
			data = json.load(f) or {}
			return {
				"tokens": _normalize_tokens(data),
				"investment": data.get("investment", DEFAULT_CONFIG["investment"]),
				"min_value": data.get("min_value", DEFAULT_CONFIG["min_value"]),
			}
	except Exception:
		return {
			"tokens": _normalize_tokens(DEFAULT_CONFIG),
			"investment": DEFAULT_CONFIG["investment"],
			"min_value": DEFAULT_CONFIG["min_value"],
		}
