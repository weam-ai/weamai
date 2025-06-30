class StreamingResponseWithStatusCodeError(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
    def generate_chunk_header(self) -> str:
        return f"{len(self.message):X}\r\n{self.message}\r\n{self.status_code}\r\n"
