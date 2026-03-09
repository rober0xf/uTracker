from enum import IntEnum, StrEnum


class DivisionEnum(StrEnum):
    FLYWEIGHT = "flyweight"
    BANTAMWEIGHT = "bantamweight"
    FEATHERWEIGHT = "featherweight"
    LIGHTWEIGHT = "lightweight"
    WELTERWEIGHT = "welterweight"
    MIDDLEWEIGHT = "middleweight"
    LIGHT_HEAVYWEIGHT = "light_heavyweight"
    HEAVYWEIGHT = "heavyweight"


class RoundsEnum(IntEnum):
    THREE = 3
    FIVE = 5


class WinningMethodEnum(StrEnum):
    DECISION = "decision"
    KO = "ko"
    TKO = "tko"
    SUBMISSION = "submission"
    DRAW = "draw"
    NC = "nc"
    DQ = "dq"
