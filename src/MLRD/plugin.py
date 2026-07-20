from typing import Annotated

from ocelescope import OCEL, OCELAnnotation, Plugin, PluginInput, plugin_method, PetriNet
from pydantic import Field

from .resource import ResourceDetection
from .utils.MLPAMiner import mlpaDiscovery
from .utils.process_area_discovery import apply
from .input import InputPA, MineInput


class ResourceDetection(Plugin):
    label = "Multi-Level Resource Detection"
    description = "Discover Level Assignment of Object Types and Groups of Object Types that are Process Areas to seperate complex data into smaller, understandable parts"
    version = "1.0.0"

    @plugin_method(label="Level Assignment and Process Areas", description="Discovers Level Assignments and Process Areas")
    def mine_mlpa(self, ocel: Annotated[OCEL, OCELAnnotation(label="Event Log")], input: MineInput) -> ResourceDetection:
        return mlpaDiscovery(ocel.ocel,input.tau)


    @plugin_method(label="Discover OCPN based on Process Areas", description="Discover Object-Centric Petri Nets based on all Process Areas at a specific Level")
    def discover_ocpn(self, ocel: Annotated[OCEL, OCELAnnotation(label="Event Log")], resource_detection:ResourceDetection, input: InputPA) -> PetriNet:
        return apply(ocel.ocel, resource_detection, input)