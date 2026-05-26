from pydantic import BaseModel, model_validator


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str

    @model_validator(mode="after")
    def validate_times(self) -> "TranscriptSegment":
        if self.start < 0:
            raise ValueError("start must be non-negative")
        if self.end < self.start:
            raise ValueError("end must be >= start")
        return self
