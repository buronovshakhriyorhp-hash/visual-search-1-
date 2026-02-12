class VisualSearchError(Exception):
    """Base exception for the application."""
    pass

class ExternalAPIError(VisualSearchError):
    """Raised when an external API (SerpApi, Cloudinary) fails."""
    pass

class ModelError(VisualSearchError):
    """Raised when the ML model fails to load or infer."""
    pass

class IndexNotFoundError(VisualSearchError):
    """Raised when the FAISS index is missing or corrupt."""
    pass
