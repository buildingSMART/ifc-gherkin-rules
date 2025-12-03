import ast
from collections import defaultdict
import os
import re
import shutil
import subprocess
import sys
import time
from typing import Any, List, Tuple, Dict

"""
Warning this is a mixture of AI and human generated code.
Code quality is low.
"""

def process(log_text):

    lines = log_text.splitlines()
    structure = defaultdict(list)

    last_step = None
    last_scenario = None
    for line in lines:
        stripped = line.strip()
        if m := re.match(r'^(Given|Then)\s+(.*)', stripped):
            last_step = m.group(2).split('#')[0].rstrip()
        elif m := re.match(r'^(Scenario|Scenario Outline)\s*:\s+(.*)', stripped):
            last_scenario = m.group(2).split('#')[0].rstrip()
        elif stripped.startswith('>'):
            if last_step is not None:
                expr = stripped.lstrip('> ').strip()
                structure[last_scenario].append((last_step, ast.literal_eval(expr)))
                last_step = None

    for ls in structure.values():
        assert len(set(len(res) for _, res in ls)) == 1

    for scenario, steps_results in structure.items():

        num_slots = next(iter(len(res) for _, res in steps_results))

        node_defs: List[Tuple[str, str]] = []
        edges: List[Tuple[str, str, str]] = []

        def register_node(node_id: str, label: str):
            node_defs.append((node_id, label))

        # Root node
        root_id = "n_root"
        register_node(root_id, "ROOT")

        # For each slot-index at level 0, start from ROOT
        slot_nodes: Dict[int, List[str]] = {i: [root_id] for i in range(num_slots)}

        # Cluster records
        # Each cluster: {
        #   'parent': Optional[int],
        #   'level': int,
        #   'slot': int,
        #   'kind': 'tuple' or 'list',
        #   'leaf_indices': List[int],         # direct atomic children
        #   'children': List[int]              # indices of child clusters
        # }
        clusters: List[Dict[str, Any]] = []

        # Traverse values to collect leaf labels and nested clusters
        def build_for_value(val: Any, level: int, slot_idx: int):
            leaf_labels: List[str] = []
            leaf_counter = 0

            def traverse(node: Any, parent_cluster_idx: int | None) -> Tuple[List[int], int | None]:
                nonlocal leaf_counter, leaf_labels

                # Atomic: None or IFC token string
                if not isinstance(node, (list, tuple)):
                    label_str = "None" if node is None else str(node)
                    idx = leaf_counter
                    leaf_counter += 1
                    leaf_labels.append(label_str)
                    return [idx], None

                # Container: list or tuple
                kind = "tuple" if isinstance(node, tuple) else "list"
                my_idx = len(clusters)
                clusters.append({
                    "parent": parent_cluster_idx,
                    "level": level,
                    "slot": slot_idx,
                    "kind": kind,
                    "leaf_indices": [],
                    "children": []
                })

                all_leaf_indices: List[int] = []
                for child in node:
                    child_leaf_indices, child_cluster_idx = traverse(child, my_idx)
                    all_leaf_indices.extend(child_leaf_indices)
                    if child_cluster_idx is None:
                        # atomic child -> direct leaves of this container
                        clusters[my_idx]["leaf_indices"].extend(child_leaf_indices)
                    else:
                        # child container -> nested cluster
                        clusters[my_idx]["children"].append(child_cluster_idx)

                return all_leaf_indices, my_idx

            leaf_indices, root_cluster_idx = traverse(val, None)
            return leaf_labels, leaf_indices, root_cluster_idx

        # Build nodes, edges, and clusters across steps and slots
        for step_idx, (step_text, struct) in enumerate(steps_results):
            level = step_idx + 1
            new_slot_nodes: Dict[int, List[str]] = {}
            for slot_idx, val in enumerate(struct):
                prev_ids = slot_nodes[slot_idx]

                leaf_labels, leaf_indices, root_cluster_idx = build_for_value(val, level, slot_idx)

                # Create nodes for each leaf; leaves are unique per occurrence
                leaf_node_ids: List[str] = []
                for leaf_idx, label in enumerate(leaf_labels):
                    node_id = f"n_{level}_{slot_idx}_{leaf_idx}"
                    register_node(node_id, label)
                    leaf_node_ids.append(node_id)

                # Edges from previous nodes to each leaf
                if len(prev_ids) == len(leaf_indices):
                    for prev_id, leaf_idx in zip(prev_ids, leaf_indices):
                        edges.append((prev_id, leaf_node_ids[leaf_idx], step_text))
                elif len(prev_ids) == 1:
                    for leaf_idx in leaf_indices:
                        edges.append((prev_ids[0], leaf_node_ids[leaf_idx], step_text))
                else:
                    raise RuntimeError("AI help me")
                
                new_slot_nodes[slot_idx] = leaf_node_ids

            slot_nodes = new_slot_nodes

        # ---- 4) Generate DOT with nested clusters for tuple/list structure ----

        def escape_label(label: str) -> str:
            return label.replace("\\", "\\\\").replace('"', '\\"')

        dot_lines: List[str] = []
        dot_lines.append("digraph gherkin_exec_tree {")
        dot_lines.append("  rankdir=LR;")
        dot_lines.append('  node [shape=rect,fontname="Helvetica"];')

        # Node definitions
        for node_id, label in node_defs:
            dot_lines.append(f'  {node_id} [label="{escape_label(label)}"];')

        # Build map from cluster index -> children, and identify roots
        cluster_children_map: Dict[int, List[int]] = {}
        cluster_parent_map: Dict[int, int | None] = {}
        for idx, c in enumerate(clusters):
            cluster_parent_map[idx] = c["parent"]
            cluster_children_map[idx] = c["children"]

        root_clusters = [idx for idx, p in cluster_parent_map.items() if p is None]

        def node_id_for_leaf(level: int, slot: int, leaf_idx: int) -> str:
            return f"n_{level}_{slot}_{leaf_idx}"

        # Recursive emission of cluster subgraphs
        def emit_cluster(idx: int, indent: int = 2):
            c = clusters[idx]
            indent_str = " " * indent
            cid = f"cluster_{idx}"
            kind = c["kind"]
            level = c["level"]
            slot = c["slot"]
            label = f"{kind} (level {level}, slot {slot})"

            dot_lines.append(f'{indent_str}subgraph {cid} {{')
            dot_lines.append(f'{indent_str}  style=solid;')

            # direct leaf nodes in this container
            for leaf_idx in c["leaf_indices"]:
                nid = node_id_for_leaf(level, slot, leaf_idx)
                dot_lines.append(f"{indent_str}  {nid};")

            # nested clusters
            for child_idx in c["children"]:
                emit_cluster(child_idx, indent + 2)

            dot_lines.append(f"{indent_str}}}")

        # Emit all root-level clusters
        for root_c in root_clusters:
            emit_cluster(root_c)

        # Edges
        for src_id, dst_id, elabel in edges:
            dot_lines.append(f'  {src_id} -> {dst_id} [label="{escape_label(elabel)}"];')

        dot_lines.append("}")
        dot_text = "\n".join(dot_lines)

        yield scenario, dot_text


if __name__ == "__main__":
    assert shutil.which("dot")

    assert os.path.exists(sys.argv[1])
    assert sys.argv[1].endswith(".feature")

    fn = next(iter(v for v in sys.argv if v.startswith("input=")), None)
    assert fn
    fn = fn.split("=")[1]
    assert os.path.exists(fn)

    log_txt = subprocess.run([
        sys.executable,
        "-m", "behave",
        "--no-capture", "-v",
        *sys.argv[1:]],
        text=True, capture_output=True
    ).stdout

    feature = os.path.basename(sys.argv[1])[0:6]

    for scn, dot_text in process(log_txt):
        scn = ''.join(c for c in scn if c.isalnum())
        ofn = f"{feature}_{scn}_{os.path.basename(fn)}.dot"
        with open(ofn, "w") as f:
            f.write(dot_text)
        time.sleep(1.)
        subprocess.run([shutil.which("dot"), ofn, "-Tpng", "-O"])
        