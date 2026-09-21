"""Domain-level exceptions shared across layers."""


class DomainError(Exception):
    """Base class for business-rule violations."""


class EntityNotFoundError(DomainError):
    """Raised when an aggregate cannot be located."""


class EntityAlreadyExistsError(DomainError):
    """Raised when a uniqueness constraint would be violated."""


class AuthenticationError(DomainError):
    """Raised when credentials are invalid."""
