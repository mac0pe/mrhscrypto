from dataclasses import dataclass

@dataclass(frozen=True)
class MRHSParameters:
    d: int
    security: int
    n: int
    m: int