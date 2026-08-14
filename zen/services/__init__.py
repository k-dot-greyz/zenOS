"""zenOS application services shared by CLI and HTTP."""

from zen.services.errors import NotFoundError, ServiceError, UnavailableError

__all__ = ["NotFoundError", "ServiceError", "UnavailableError"]
