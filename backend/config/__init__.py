import os

def getenv(key, default=None):
    """Read a value from the environment, falling back to a default."""
    return os.environ.get(key, default)