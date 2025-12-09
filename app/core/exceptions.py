class CADException(Exception):
    """Базовое исключение для CAD операций."""
    pass

class CADConnectionError(CADException):
    """Ошибка подключения к CAD системе."""
    pass

class CADShapeCreationError(CADException):
    """Ошибка создания фигуры."""
    pass