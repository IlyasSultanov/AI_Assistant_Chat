class BaseEx(Exception):
    def __init__(self, status_code, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(self.status_code, self.message)

    def to_dict(self):
        return {"status_code": self.status_code, "message": self.message}


class AuthException(BaseEx):
    pass


class ForbiddenException(BaseEx):
    pass


class BadRequestException(BaseEx):
    pass
