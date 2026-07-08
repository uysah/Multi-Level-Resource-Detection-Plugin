from ocelescope.discovery.decorator import discovery_method
from ocelescope.resource.default.petri_net import PetriNet
from pydantic import Field
from typing import Annotated
from ocelescope import OCEL


from .resource import ResourceDetection
from .utils.MLPAMiner import mlpaDiscovery

@discovery_method(
    name="Multi-Level Resource Detection",
    description="Discover Level Assignment of Object Types and Groups of Object Types that are Process Areas to seperate complex data into smaller, understandable parts",
)
def discover_mlrd(
    ocel:OCEL,
    tau: Annotated[
        float,
        Field(
            ge=0,
            le=1,
            default=0.9,
            title="Support Threshold (τ)",
            description=(
                "Minimum fraction of observations supporting a cardinality or temporal "
                "relation for it to be included. Higher values filter more noise."
            ),
        ),
    ] = 0.9,
) -> ResourceDetection:
    return mlpaDiscovery(ocel.ocel,tau)
