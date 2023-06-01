from .agr_cro_client import ShapeshifterAgrCroClient
from .agr_dso_client import ShapeshifterAgrDsoClient
from .cro_agr_client import ShapeshifterCroAgrClient
from .cro_dso_client import ShapeshifterCroDsoClient
from .dso_agr_client import ShapeshifterDsoAgrClient
from .dso_cro_client import ShapeshifterDsoCroClient

__all__ = [
    "ShapeshifterAgrCroClient",
    "ShapeshifterAgrDsoClient",
    "ShapeshifterCroAgrClient",
    "ShapeshifterCroDsoClient",
    "ShapeshifterDsoAgrClient",
    "ShapeshifterDsoCroClient"
]

client_map = {
    (client.sender_role, client.recipient_role): client
    for client in [globals()[name] for name in __all__]
}
