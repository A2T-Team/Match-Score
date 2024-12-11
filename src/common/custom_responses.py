from fastapi import Response
from starlette.responses import JSONResponse


class BadRequest(JSONResponse):
    def __init__(self, content=""):
        super().__init__(status_code=400, content={"detail": content})
        self.content = content


class Locked(JSONResponse):
    def __init__(self, content=""):
        super().__init__(status_code=400, content={"detail": f"{content} is locked"})


class Unauthorized(JSONResponse):
    def __init__(self, content=""):
        super().__init__(status_code=401, content={"detail": content})


class ForbiddenAccess(JSONResponse):
    def __init__(self, content="You don't have permission to access this resource"):
        super().__init__(status_code=403, content={"detail": content})


class OnlyAdminAccess(JSONResponse):
    def __init__(self, content=""):
        super().__init__(
            status_code=403, content={"detail": f"Only admin can {content}"}
        )


class OnlyAuthorAccess(JSONResponse):
    def __init__(self, content=""):
        super().__init__(
            status_code=403, content={"detail": f"Only the author can {content}"}
        )


class NotFound(JSONResponse):
    def __init__(self, key: str, key_value: str):
        super().__init__(
            status_code=404, content={"detail": f"{key} '{key_value}' not found."}
        )


class AlreadyExists(JSONResponse):
    def __init__(self, content=""):
        super().__init__(
            status_code=409, content={"detail": f"{content} already exists"}
        )


class OK(JSONResponse):
    def __init__(self, content=""):
        super().__init__(status_code=200, content={"detail": content})


class Created(JSONResponse):
    def __init__(self, content=""):
        super().__init__(status_code=201, content={"detail": content})


class NoContent(Response):
    def __init__(self):
        super().__init__(status_code=204)


class InternalServerError(JSONResponse):
    def __init__(self, content="An unexpected error occurred"):
        super().__init__(status_code=500, content={"detail": content})
