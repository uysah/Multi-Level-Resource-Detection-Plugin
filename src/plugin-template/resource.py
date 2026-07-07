from typing import Literal

from ocelescope import Resource
from ocelescope.visualization.default.graph import (
    EdgeArrow,
    Graph,
    GraphEdge,
    GraphNode,
    GraphvizLayoutConfig,
    ElkLayoutConfig
)
from ocelescope.visualization.util.color import generate_color_map
from pydantic import BaseModel
from typing import Dict, Set,FrozenSet

Temporal_Relation_Constant = Literal["D", "Di", "I", "Ii", "P"]

Cardinality = Literal["0", "1", "0...1", "1..*", "0...*"]

# Force-directed layout tuned to spread object types further apart.
# `K` raises the ideal edge length and `sep` adds margin around each node so
# the graph reads as spaced out rather than clustered.
TOTEM_GRAPH_LAYOUT = GraphvizLayoutConfig(
    engine="sfdp",
    graphAttrs={
        "overlap": "false",
        "splines": "spline",
        "K": 2.4,
        "repulsiveforce": 3.0,
        "sep": "+60",
    },
)


class TotemEdge(BaseModel):
    source: str
    target: str
    lc: Cardinality | None
    lc_inverse: Cardinality | None
    ec: Cardinality | None
    ec_inverse: Cardinality | None
    tr: Temporal_Relation_Constant | None
    tr_inverse: Temporal_Relation_Constant | None


class Totem(Resource):
    label = "TOTeM"
    description = "A TOTeM"

    object_types: list[str]
    edges: list[TotemEdge]
    type: Literal["totem"] = "totem"

    def visualize(self) -> Graph:
        def tr_to_arrow(tr: Temporal_Relation_Constant | None) -> EdgeArrow:
            mapping: dict[Temporal_Relation_Constant | None, EdgeArrow] = {
                "P": "triangle",
                "D": "tee",
                "I": "circle",
                "Ii": None,
                "Di": None,
                None: None,
            }
            return mapping[tr]

        def edge_label_for_forward(e: TotemEdge) -> str:
            parts = []
            if e.ec:
                parts.append(e.ec)
            if e.ec_inverse:
                parts.append(e.ec_inverse)
            return " · ".join(parts) if parts else ""

        color_map = generate_color_map(self.object_types)
        nodes: list[GraphNode] = []
        for ot in self.object_types:
            nodes.append(
                GraphNode(
                    id=ot,
                    label=ot,
                    shape="rectangle",
                    color=color_map.get(ot),
                    width=max(90.0, len(ot) * 8.0 + 24.0),
                    height=40,
                )
            )

        edges: list[GraphEdge] = []
        for e in self.edges:
            src_arrow = tr_to_arrow(e.tr_inverse)
            tgt_arrow = tr_to_arrow(e.tr)
            label = edge_label_for_forward(e)
            color = color_map.get(e.source)

            edges.append(
                GraphEdge(
                    source=e.source,
                    target=e.target,
                    start_arrow=src_arrow,
                    end_arrow=tgt_arrow,
                    color=color,
                    label=label,
                    end_label=e.lc,
                    start_label=e.lc_inverse,
                )
            )

        return Graph(
            type="graph",
            nodes=nodes,
            edges=edges,
            layout_config=TOTEM_GRAPH_LAYOUT,
        )
    

class ResourceDetection(Resource):
    label = "Resource Detection"
    description = "Multi-Level Resource Detection Graph"

    object_types_to_layer: Dict[float, Set[str]]
    type_relations: list[TotemEdge]

   

    def visualize(self) -> Graph:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        
        color_map = generate_color_map(list(self.object_types_to_layer.keys()))
        def tr_to_arrow(tr: Temporal_Relation_Constant | None) -> EdgeArrow:
            mapping: dict[Temporal_Relation_Constant | None, EdgeArrow] = {
                "P": "triangle",
                "D": "tee",
                "I": "circle",
                "Ii": None,
                "Di": None,
                None: None,
            }
            return mapping[tr]

        neighbors: dict[str, set[str]] = {}
        for e in self.type_relations:
            neighbors.setdefault(e.source, set()).add(e.target)
            neighbors.setdefault(e.target, set()).add(e.source)

        sorted_levels = sorted(self.object_types_to_layer.keys())
        color_map = generate_color_map([str(level) for level in sorted_levels])

        y_gap = 150.0
        x_gap = 180.0

        node_x: dict[str, float] = {}
        node_y: dict[str, float] = {}
        node_width: dict[str, float] = {}

        for level in sorted_levels:
            types_this_level = list(self.object_types_to_layer[level])

            def sort_key(obj_type: str) -> tuple[float, str]:
                placed = [node_x[n] for n in neighbors.get(obj_type, ()) if n in node_x]
                if placed:
                    return (sum(placed) / len(placed), obj_type)
                return (float("inf"), obj_type)

            types_this_level.sort(key=sort_key)

            x = 0.0
            for obj_type in types_this_level:
                width = max(90.0, len(obj_type) * 8.0 + 24.0)
                node_x[obj_type] = x
                node_y[obj_type] = level * y_gap
                node_width[obj_type] = width
                x += width + x_gap

        nodes: list[GraphNode] = []
        label_x_offset = -220.0
        for level in sorted_levels:
            for obj_type in sorted(self.object_types_to_layer[level]):
                x, y = node_x[obj_type], node_y[obj_type]
                nodes.append(
                    GraphNode(
                        id=obj_type,
                        label=obj_type,
                        shape="rectangle",
                        width=node_width[obj_type],
                        height=40,
                        x=x,
                        y=y,
                        color=color_map.get(str(level)),
                        rank=int(level),
                        layout_attrs={"pos": f"{x},{y}!"},
                    )
                )

            label_y = level * y_gap
            nodes.append(
                GraphNode(
                    id=f"__level_label_{level}",
                    label=f"Level {int(level)}",
                    shape="rectangle",      
                    width=80.0,
                    height=40.0,
                    x=label_x_offset,
                    y=label_y,
                    color=None,
                    border_color="#a9c9ec",     
                    layout_attrs={"pos": f"{label_x_offset},{label_y}!"},
                )
            )

        edges: list[GraphEdge] = []
        for e in self.type_relations:
            src_arrow = tr_to_arrow(e.tr_inverse)
            tgt_arrow = tr_to_arrow(e.tr)
            edges.append(
                GraphEdge(
                    source=e.source,
                    target=e.target,
                    start_arrow=src_arrow,
                    end_arrow=tgt_arrow,
                )
            )

        graph = Graph(
            nodes=nodes,
            edges=edges,
            layout_config=GraphvizLayoutConfig(
                engine="neato",
                graphAttrs={
                    "overlap": "false",
                    "splines": "true",
                    "inputscale": "72",
                    "esep": "+20",  
                },
            ),
        )
        print(nodes)
        return graph

    def all_object_types(self) -> Set[str]:
        result: list = []
        for types in self.object_types_to_layer.values():
            result.append(types) 
        return set(result)