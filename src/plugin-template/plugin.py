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
    description = ""
    version = "1.0"

    @plugin_method(label="Example", description="Example")
    def mine_totem(self, ocel: Annotated[OCEL, OCELAnnotation(label="Event Log")], input: MineInput) -> ResourceDetection:
        return mlpaDiscovery(ocel.ocel,input.tau)
