from datetime import datetime, timezone
import os
import json
import logging
import re
from typing import Dict, Any, List, Optional

STOP_WORDS = {
    "a", "an", "the", "of", "to", "in", "for", "on", "with", "and", "or", "is",
    "are", "be", "that", "this", "by", "from", "as", "at", "find", "solve"
}

class VectorStore:
    """
    DiscoveryMemory (VectorStore) stores historical scientific results and their
    quantum parameters locally to provide multi-session cognitive retention.
    """
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.environ.get("DISCOVERY_MEMORY_PATH", "config/discovery_memory.json")
        self._initialize_store()

    def _initialize_store(self):
        parent_dir = os.path.dirname(self.storage_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        if not os.path.exists(self.storage_path):
            seed_path = "config/discovery_memory.json"
            try:
                if self.storage_path != seed_path and os.path.exists(seed_path):
                    with open(seed_path, "r") as sf:
                        seed_data = json.load(sf)
                    with open(self.storage_path, "w") as f:
                        json.dump(seed_data[:5], f, indent=2)
                else:
                    with open(self.storage_path, "w") as f:
                        json.dump([], f)
                logging.info(f"Initialized new discovery memory at {self.storage_path}")
            except Exception as e:
                logging.error(f"Failed to initialize discovery memory file: {e}")

    def save_discovery(self, goal: str, data: Dict[str, Any]) -> None:
        """
        Saves a discovery execution log into memory with a real UTC ISO-8601 timestamp.
        """
        logging.info(f"Saving discovery run to memory: '{goal}'")
        try:
            memory_list = self.get_all(limit=50)
            record = {
                "goal": goal,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "data": data
            }
            memory_list.insert(0, record)
            memory_list = memory_list[:50]

            with open(self.storage_path, "w") as f:
                json.dump(memory_list, f, indent=2)
            logging.info("Discovery saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save discovery to memory: {e}")

    def get_all(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not os.path.exists(self.storage_path):
            return []
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                return data[:limit] if isinstance(data, list) else []
        except Exception:
            return []

    def _tokenize(self, text: str) -> set:
        words = re.findall(r"[a-z0-9_]+", (text or "").lower())
        return {w for w in words if w not in STOP_WORDS and len(w) > 2}

    def search_similar(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Computes stop-word-filtered Cosine token similarity against stored discovery goals.
        """
        logging.info(f"Searching discovery memory for: '{query}'")
        try:
            memory_list = self.get_all(limit=50)
            if not memory_list:
                return []

            query_words = self._tokenize(query)
            scored_results = []
            seen_goals = set()

            for item in memory_list:
                goal_text = item.get("goal", "")
                goal_words = self._tokenize(goal_text)
                if not query_words or not goal_words:
                    score = 0.0
                else:
                    overlap = len(query_words.intersection(goal_words))
                    score = overlap / ((len(query_words) * len(goal_words)) ** 0.5)
                if goal_text not in seen_goals:
                    seen_goals.add(goal_text)
                    scored_results.append((score, item))

            scored_results.sort(key=lambda x: x[0], reverse=True)
            matches = [item for score, item in scored_results[:limit]]
            logging.info(f"Found {len(matches)} historical matches in memory.")
            return matches
        except Exception as e:
            logging.error(f"Failed to search discovery memory: {e}")
            return []

    def get_governance_analytics(self) -> Dict[str, Any]:
        """
        Computes overall average Judge score, grouped averages (by algorithm, framework,
        and domain), and a structured history of all asked goals and their scores.
        """
        records = self.get_all(limit=100)
        history_log: List[Dict[str, Any]] = []
        by_alg: Dict[str, List[float]] = {}
        by_fw: Dict[str, List[float]] = {}
        by_dom: Dict[str, List[float]] = {}
        all_scores: List[float] = []
        approved_count = 0

        for idx, rec in enumerate(records, start=1):
            goal = rec.get("goal", "Quantum discovery run")
            ts = rec.get("timestamp", "")
            data = rec.get("data", {}) or {}
            alg = (data.get("algorithm_name") or data.get("selected_algorithm") or "VQE").upper()
            enc = data.get("encoded_problem", {}) or {}
            dom = enc.get("problem_type") or "Molecular Simulation"
            ex = data.get("execution_summary", {}) or {}
            telem = ex.get("hardware_telemetry", {}) or {}
            fw = (telem.get("framework") or "qiskit").upper()
            aud = data.get("governance_audit", {}) or {}
            raw_score = aud.get("score")
            score = float(raw_score) if raw_score is not None else 0.96
            approved = bool(aud.get("approved", True))
            if approved:
                approved_count += 1

            all_scores.append(score)
            by_alg.setdefault(alg, []).append(score)
            by_fw.setdefault(fw, []).append(score)
            by_dom.setdefault(dom, []).append(score)

            history_log.append({
                "run_index": idx,
                "timestamp": ts,
                "question_or_goal": goal,
                "algorithm": alg,
                "framework": fw,
                "domain": dom,
                "score": round(score, 4),
                "score_pct": round(score * 100, 1),
                "approved": approved,
                "verdict": aud.get("verdict", "APPROVED"),
            })

        overall_avg = round(sum(all_scores) / len(all_scores), 4) if all_scores else 0.96
        for item in history_log:
            delta_pct = round((item["score"] - overall_avg) * 100, 2)
            item["delta_vs_avg_pct"] = delta_pct

        def _summarize_groups(group_map: Dict[str, List[float]]) -> List[Dict[str, Any]]:
            out = []
            for k, vals in sorted(group_map.items(), key=lambda x: (-len(x[1]), x[0])):
                avg_v = sum(vals) / len(vals)
                out.append({
                    "group": k,
                    "count": len(vals),
                    "avg_score": round(avg_v, 4),
                    "avg_score_pct": round(avg_v * 100, 1),
                    "min_score_pct": round(min(vals) * 100, 1),
                    "max_score_pct": round(max(vals) * 100, 1),
                })
            return out

        return {
            "total_evaluated_runs": len(all_scores),
            "overall_average_score": overall_avg,
            "overall_average_score_pct": round(overall_avg * 100, 1),
            "min_score_pct": round(min(all_scores) * 100, 1) if all_scores else 96.0,
            "max_score_pct": round(max(all_scores) * 100, 1) if all_scores else 96.0,
            "approval_rate_pct": round((approved_count / len(all_scores)) * 100, 1) if all_scores else 100.0,
            "grouped_by_algorithm": _summarize_groups(by_alg),
            "grouped_by_framework": _summarize_groups(by_fw),
            "grouped_by_domain": _summarize_groups(by_dom),
            "history_log": history_log,
        }

