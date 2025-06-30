class OpenAIError(Exception):
    """Base class for OpenAI-related errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class LengthFinishReasonError(OpenAIError):
    def __init__(self) -> None:
        super().__init__(
            "Could not parse response content as the length limit was reached"
        )

class ContentFilterFinishReasonError(OpenAIError):
    def __init__(self) -> None:
        super().__init__(
            "Could not parse response content as the request was rejected by the content filter"
        )
