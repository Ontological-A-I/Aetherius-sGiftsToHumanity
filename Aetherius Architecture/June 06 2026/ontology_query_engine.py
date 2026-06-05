# ===== FILE: services/ontology_query_engine.py =====
import os
import json
from collections import deque
import services.config as config


class OntologyQueryEngine:
    """
    Graph-traversal engine over Aetherius's A-SMDL semantic network.

    Reads from OntologyArchitect's supertoken_legend.jsonl and builds
    an in-memory adjacency map keyed by concept name / SQT token.
    Provides BFS graph walks, path finding, and concept clustering.
    """

    def __init__(self, data_directory=None):
        self.data_directory = data_directory or config.DATA_DIR
        self.legend_file = os.path.join(self.data_directory, "supertoken_legend.jsonl")
        self.index_file = os.path.join(self.data_directory, "ontology_index.json")
        self.graph: dict = {}      # concept → {definition, domain, related_concepts[]}
        self._loaded = False
        print("[OntologyQueryEngine] Semantic query engine online.", flush=True)

    # ── Graph construction ────────────────────────────────────────────────────

    def _ensure_loaded(self):
        """Lazy-loads the graph on first query so boot time is unaffected."""
        if self._loaded:
            return
        self._load_from_legend()
        self._load_from_index()
        self._loaded = True

    def _load_from_legend(self):
        """Ingests supertoken_legend.jsonl — the richest source of concept data."""
        if not os.path.exists(self.legend_file):
            return
        try:
            with open(self.legend_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    # SQT entries use 'sqt' as the primary key
                    key = (entry.get("sqt") or entry.get("term") or "").strip()
                    if not key:
                        continue
                    related = entry.get("related_concepts", [])
                    if isinstance(related, str):
                        related = [r.strip() for r in related.split(",") if r.strip()]
                    self.graph[key] = {
                        "definition": entry.get("definition", ""),
                        "domain": entry.get("domain", ""),
                        "related_concepts": list(related),
                        "source": "legend",
                    }
        except Exception as e:
            print(f"[OntologyQueryEngine] WARNING loading legend: {e}", flush=True)

    def _load_from_index(self):
        """Supplements with ontology_index.json if present."""
        if not os.path.exists(self.index_file):
            return
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                index = json.load(f)
            if isinstance(index, dict):
                for key, data in index.items():
                    if key not in self.graph:
                        related = data.get("related_concepts", [])
                        if isinstance(related, str):
                            related = [r.strip() for r in related.split(",") if r.strip()]
                        self.graph[key] = {
                            "definition": data.get("definition", ""),
                            "domain": data.get("domain", ""),
                            "related_concepts": list(related),
                            "source": "index",
                        }
        except Exception as e:
            print(f"[OntologyQueryEngine] WARNING loading index: {e}", flush=True)

    def reload(self):
        """Forces a full reload on next query — call after OntologyArchitect writes."""
        self._loaded = False
        self.graph = {}

    # ── Query API ─────────────────────────────────────────────────────────────

    def query_graph(self, start_concept: str, max_depth: int = 3) -> dict:
        """
        BFS from start_concept, returning all reachable nodes up to max_depth.
        Returns a dict of {concept: node_data} for every visited node.
        """
        self._ensure_loaded()
        start = start_concept.strip()
        if start not in self.graph:
            # Case-insensitive fallback
            match = next((k for k in self.graph if k.lower() == start.lower()), None)
            if not match:
                return {"error": f"Concept '{start_concept}' not found in ontology.",
                        "graph_size": len(self.graph)}
            start = match

        visited: dict = {}
        queue = deque([(start, 0)])
        seen = {start}

        while queue:
            concept, depth = queue.popleft()
            node = self.graph.get(concept)
            if not node:
                continue
            visited[concept] = {**node, "depth_from_start": depth}
            if depth < max_depth:
                for neighbour in node.get("related_concepts", []):
                    neighbour = neighbour.strip()
                    if neighbour and neighbour not in seen and neighbour in self.graph:
                        seen.add(neighbour)
                        queue.append((neighbour, depth + 1))

        return {
            "start": start,
            "max_depth": max_depth,
            "nodes_found": len(visited),
            "subgraph": visited,
        }

    def find_path(self, concept_a: str, concept_b: str) -> dict:
        """
        BFS shortest path between two concepts.
        Returns the path as an ordered list of concept names, or an empty list
        if no path exists within the graph.
        """
        self._ensure_loaded()
        a = concept_a.strip()
        b = concept_b.strip()

        # Case-insensitive matching
        keys_lower = {k.lower(): k for k in self.graph}
        a = keys_lower.get(a.lower(), a)
        b = keys_lower.get(b.lower(), b)

        if a not in self.graph:
            return {"error": f"Start concept '{concept_a}' not found.", "path": []}
        if b not in self.graph:
            return {"error": f"End concept '{concept_b}' not found.", "path": []}
        if a == b:
            return {"path": [a], "length": 0}

        # Standard BFS with parent tracking
        parent = {a: None}
        queue = deque([a])
        found = False

        while queue and not found:
            current = queue.popleft()
            for neighbour in self.graph.get(current, {}).get("related_concepts", []):
                neighbour = neighbour.strip()
                if not neighbour or neighbour not in self.graph:
                    continue
                if neighbour not in parent:
                    parent[neighbour] = current
                    if neighbour == b:
                        found = True
                        break
                    queue.append(neighbour)

        if not found:
            return {"path": [], "length": -1,
                    "message": f"No path found between '{a}' and '{b}'."}

        # Reconstruct path
        path = []
        node = b
        while node is not None:
            path.append(node)
            node = parent[node]
        path.reverse()
        return {"path": path, "length": len(path) - 1}

    def cluster_around(self, concept: str) -> dict:
        """
        Returns the immediate neighbourhood of a concept:
        the concept itself, all its direct neighbours, and their domains.
        Useful for contextual understanding without deep traversal.
        """
        self._ensure_loaded()
        key = concept.strip()
        keys_lower = {k.lower(): k for k in self.graph}
        key = keys_lower.get(key.lower(), key)

        if key not in self.graph:
            return {"error": f"Concept '{concept}' not found.", "cluster": {}}

        center = self.graph[key]
        cluster = {key: {**center, "role": "center"}}

        for neighbour in center.get("related_concepts", []):
            neighbour = neighbour.strip()
            if neighbour and neighbour in self.graph:
                cluster[neighbour] = {**self.graph[neighbour], "role": "neighbour"}

        return {
            "center": key,
            "cluster_size": len(cluster),
            "cluster": cluster,
        }

    def search_by_domain(self, domain: str) -> list:
        """Returns all concepts belonging to a given domain string."""
        self._ensure_loaded()
        domain_lower = domain.lower()
        return [
            {"concept": k, "definition": v.get("definition", ""),
             "related_concepts": v.get("related_concepts", [])}
            for k, v in self.graph.items()
            if domain_lower in v.get("domain", "").lower()
        ]

    def stats(self) -> dict:
        """Returns a summary of the loaded ontology graph."""
        self._ensure_loaded()
        total_edges = sum(len(v.get("related_concepts", [])) for v in self.graph.values())
        domains = {}
        for v in self.graph.values():
            d = v.get("domain", "unknown") or "unknown"
            domains[d] = domains.get(d, 0) + 1
        return {
            "total_concepts": len(self.graph),
            "total_edges": total_edges,
            "domains": domains,
        }
