
class AppError(Exception):
    pass

class TableExists(AppError):
    pass

class KeyNotExist(AppError):
    pass