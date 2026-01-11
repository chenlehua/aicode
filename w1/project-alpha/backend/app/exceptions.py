"""Custom exceptions."""

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """Resource not found exception."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": f"{resource.upper()}_NOT_FOUND",
                "message": f"{resource} not found: {resource_id}",
            },
        )


class TicketNotFoundError(NotFoundError):
    """Ticket not found exception."""

    def __init__(self, ticket_id: str):
        super().__init__("TICKET", ticket_id)


class TagNotFoundError(NotFoundError):
    """Tag not found exception."""

    def __init__(self, tag_id: str):
        super().__init__("TAG", tag_id)


class TagNameExistsError(HTTPException):
    """Tag name already exists exception."""

    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "TAG_NAME_EXISTS",
                "message": f"Tag name already exists: {name}",
            },
        )


class ValidationError(HTTPException):
    """Validation error exception."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "VALIDATION_ERROR",
                "message": message,
            },
        )
