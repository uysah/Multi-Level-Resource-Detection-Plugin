from typing import Annotated

from ocelescope import OCEL, OCELAnnotation, Plugin, PluginInput, plugin_method
from pydantic import Field

from .resource import ResourceDetection
from .utils.MLPAMiner import mlpaDiscovery


class MineInput(PluginInput):
    tau: Annotated[
        float,
        Field(
            gt=0,
            le=1,
            default=0.9,
            title="Support Threshold (τ)",
            description=(
                "Minimum fraction of observations supporting a cardinality or temporal "
                "relation for it to be included. Higher values filter more noise."
            ),
        ),
    ] = 0.9


class ResourceDetection(Plugin):
    label = "Multi-Level Resource Detection"
    description = "Discover Level Assignment of Object Types and Groups of Object Types that are Process Areas to seperate complex data into smaller, understandable parts"
    version = "1.0"

    @plugin_method(label="Level Assignment and Process Areas", description="Discovers Level Assignments and Process Areas")
    def mine_totem(self, ocel: Annotated[OCEL, OCELAnnotation(label="Event Log")], input: MineInput) -> ResourceDetection:
        return mlpaDiscovery(ocel.ocel,input.tau)
