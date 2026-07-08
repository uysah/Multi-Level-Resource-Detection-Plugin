from ocelescope import PluginInput
from pydantic import Field
from typing import Annotated

class InputPA(PluginInput):
    level: int = Field(
        default = 0,
        ge=0,
        title='Level',
        description='Select the Level Assignment to analyze'
    )

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