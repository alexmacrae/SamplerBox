class Error(Exception):
    """Base class for other exceptions"""
    pass

class WaveReadError(Error):
    pass

class NoteOnError(Error):
    pass
