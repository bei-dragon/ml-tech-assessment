class TranscriptNotFoundError(Exception):
    """Raised when a transcript analysis is not found in the repository."""
    pass

class InvalidTranscriptError(ValueError):
    """Raised when the provided transcript text is invalid (e.g., empty)."""
    pass