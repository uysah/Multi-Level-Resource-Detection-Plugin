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
    
        for level, object_types in self.object_types_to_layer.items():
            for obj_type in sorted(object_types):
                nodes.append(
                    GraphNode(
                        id=obj_type,
                        label=obj_type,
                        shape="rectangle",
                        width=max(90.0, len(obj_type) * 8.0 + 24.0),
                        height=40,
                        color=color_map.get(level),
                        rank=int(level),
                        layout_attrs={"elk.layered.layering.layerId": str(int(level))},
                    )
                )
        
        for e in self.type_relations:
            src_arrow = tr_to_arrow(e.tr_inverse)
            tgt_arrow = tr_to_arrow(e.tr)
            edges.append(
                GraphEdge(
                    source=e.source,
                    target=e.target,
                    start_arrow=src_arrow,
                    end_arrow=tgt_arrow,
                    layout_attrs={"constraint": False},
                )
            )

        layout_config = ElkLayoutConfig(
                options={
                    "elk.algorithm": "layered",
                    "elk.direction": "UP",
                    "elk.spacing.nodeNode": "80",
                    "elk.layered.spacing.nodeNodeBetweenLayers": "150",
                    "elk.spacing.edgeNode": "40",
                    "elk.layered.spacing.edgeNodeBetweenLayers": "40",
                    "elk.spacing.edgeEdge": "20",
                    "elk.layered.spacing.edgeEdgeBetweenLayers": "20",
                    "elk.padding": "[top=40,left=40,bottom=40,right=40]",
                    "elk.spacing.labelNode": "10",
                    "elk.spacing.edgeLabel": "10",
                    "elk.spacing.componentComponent": "100",
                    "elk.edgeRouting": "SPLINES",  
                }
            )
        print(nodes)
        print(edges)

        return Graph(nodes=nodes,edges=edges,layout_config=layout_config)

    def all_object_types(self) -> Set[str]:
        result: list = []
        for types in self.object_types_to_layer.values():
            result.append(types) 
        return set(result)