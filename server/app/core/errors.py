from __future__ import annotations


class ModuleNotImplementedError(NotImplementedError):
    def __init__(self, module: str, operation: str) -> None:
        super().__init__(f"{module}.{operation} is not implemented yet.")
        self.module = module
        self.operation = operation


def not_implemented(module: str, operation: str) -> None:
    raise ModuleNotImplementedError(module, operation)
