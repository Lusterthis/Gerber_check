from pydantic import BaseModel


class ProcessResponse(BaseModel):
    convertedGerber: str  # base64-encoded image
    anomalyImage: str     # base64-encoded image
    anomalyScore: float
    defectDescription: str




