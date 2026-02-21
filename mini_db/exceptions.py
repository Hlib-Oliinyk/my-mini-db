
class AppError(Exception):
    pass

class TableExists(AppError):
    pass

class KeyNotExist(AppError):
    pass

class RowNotExists(AppError):
    pass

class MultipleObjectReturn(AppError):
    pass