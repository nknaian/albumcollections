class musicorgException(Exception):
    def __init__(self, message, redirect_location=None) -> None:
        super().__init__(message)

        self._redirect_location = redirect_location


class musicorgError(musicorgException):
    pass


class musicorgAlert(musicorgException):
    pass
