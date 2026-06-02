class RecommenderError(Exception):
    """Base exception for the recommendation service."""


class ArtifactsMissingError(RecommenderError):
    """Raised when generated artifacts are missing."""


class MovieNotFoundError(RecommenderError):
    """Raised when a movie title cannot be matched."""


class UserNotFoundError(RecommenderError):
    """Raised when a user id cannot be matched."""

