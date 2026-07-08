from pm4py.objects.ocel.obj import OCEL
from ..resource import ResourceDetection
from ..input import InputPA
import pm4py
from ocelescope import PetriNet
from pm4py.objects.ocpn.obj import OCPetriNet as ObjectCentricPetriNet


def apply(ocel:OCEL, resource: ResourceDetection, input: InputPA) -> PetriNet:
    level = input.level
    ocpn_array = []

    if level not in resource.process_areas_events:
            raise ValueError(
                f"Layer {level} does not exist. "
                f"Available layers: {list(resource.process_areas_events.keys())}"
            )
    
    process_areas = resource.process_areas_events[level]
    if all(len(event_types) == 0 for _, event_types in process_areas):
        raise ValueError(
            f"No events found for process area layer {level}. "
            "Cannot discover an object-centric Petri net."
        )
    for (types,event_types) in process_areas:
        sublog = pm4py.filter_ocel_event_attribute(ocel,'ocel:activity',list(event_types))
        filtered_log = pm4py.filter_ocel_object_attribute(sublog,'ocel:type',types)
        ocpn = pm4py.discover_oc_petri_net(filtered_log)
        ocpn_array.append(ocpn)
    merged_ocpns = merge_ocpns(ocpn_array)
    
    return PetriNet.from_pm4py(merged_ocpns)

def merge_ocpns(ocpn_array):
    merged = ObjectCentricPetriNet(
        name="merged_ocpn",
        places=set(),
        transitions=set(),
        arcs=set(),
        initial_marking={},
        final_marking={},
    )

    for idx, ocpn in enumerate(ocpn_array):
        place_mapping = {}
        transition_mapping = {}
        for place in ocpn.places:
            new_place = ObjectCentricPetriNet.Place(
                name=f"{place.name}_{idx}",
                object_type=place.object_type,
                properties=getattr(place, "properties", None),
            )
            merged.places.add(new_place)
            place_mapping[place] = new_place

        for transition in ocpn.transitions:

            new_transition = ObjectCentricPetriNet.Transition(
                name=f"{transition.name}_{idx}",
                label=transition.label,
                properties=getattr(transition, "properties", None),
            )
            merged.transitions.add(new_transition)
            transition_mapping[transition] = new_transition

        for arc in ocpn.arcs:
            source = (place_mapping.get(arc.source) or transition_mapping.get(arc.source))
            target = (place_mapping.get(arc.target) or transition_mapping.get(arc.target))

            new_arc = ObjectCentricPetriNet.Arc(
                source=source,
                target=target,
                object_type=arc.object_type,
                is_variable=arc.is_variable,
                properties=getattr(arc, "properties", None),
            )
            merged.arcs.add(new_arc)
            source.out_arcs.add(new_arc)
            target.in_arcs.add(new_arc)

        if ocpn.initial_marking:
            for place, tokens in ocpn.initial_marking.items():
                merged.initial_marking[
                    place_mapping[place]
                ] = tokens

        if ocpn.final_marking:
            for place, tokens in ocpn.final_marking.items():
                merged.final_marking[
                    place_mapping[place]
                ] = tokens

    return merged