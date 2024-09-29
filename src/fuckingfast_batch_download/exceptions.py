class RateLimited(Exception):
    pass


class FileNotFound(Exception):
    def __init__(self, *args: object, filename: str) -> None:
        super().__init__(*args)
        self.filename = filename
