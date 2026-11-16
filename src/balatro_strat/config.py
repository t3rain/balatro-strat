"""Game configuration: hand types, the scoring table, and blind parameters.
"""

from dataclasses import dataclass
from enum import IntEnum
from types import MappingProxyType
from collections.abc import Mapping


class HandType(IntEnum):
    """Hand types in poker ranking order (higher value = stronger hand).

    Classification uses this order, not the scoring table: a hand that is both
    a straight and a flush is a Straight Flush even if a levelled-up Flush
    would score more (see docs/rules.MD).
    """

    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    FIVE_OF_A_KIND = 9
    FLUSH_HOUSE = 10
    FLUSH_FIVE = 11

    @property
    def label(self) -> str:
        """Hand name formatting."""
        return self.name.replace("_", " ").title().replace(" Of ", " of ").replace(" A ", " a ")


# Hands that need duplicate cards, so they cannot occur with an unmodified deck.
DUPLICATE_ONLY_HANDS = frozenset(
    {HandType.FIVE_OF_A_KIND, HandType.FLUSH_HOUSE, HandType.FLUSH_FIVE}
)


@dataclass(frozen=True)
class HandValue:
    """Base chips and mult for one hand type."""

    chips: int
    mult: int

    def __post_init__(self) -> None:
        if self.chips < 0 or self.mult < 1:
            raise ValueError(f"invalid hand value: {self}")


# Level-1 values, verified in-game (see docs/rules.MD).
# Read-only view of the dict for the hand-table.
DEFAULT_HAND_TABLE: Mapping[HandType, HandValue] = MappingProxyType(
    {
        HandType.HIGH_CARD: HandValue(5, 1),
        HandType.PAIR: HandValue(10, 2),
        HandType.TWO_PAIR: HandValue(20, 2),
        HandType.THREE_OF_A_KIND: HandValue(30, 3),
        HandType.STRAIGHT: HandValue(30, 4),
        HandType.FLUSH: HandValue(35, 4),
        HandType.FULL_HOUSE: HandValue(40, 4),
        HandType.FOUR_OF_A_KIND: HandValue(60, 7),
        HandType.STRAIGHT_FLUSH: HandValue(100, 8),
        HandType.FIVE_OF_A_KIND: HandValue(120, 12),
        HandType.FLUSH_HOUSE: HandValue(140, 14),
        HandType.FLUSH_FIVE: HandValue(160, 16),
    }
)

# Ante-1 chip targets (small, big and boss with effects disabled): reference points
# on the target grid. The target itself is an experiment parameter, not config.
ANTE1_TARGETS: tuple[int, int, int] = (300, 450, 600)


@dataclass(frozen=True)
class Config:
    """Rules for one blind."""

    hand_size: int = 8
    hands: int = 4
    discards: int = 3
    max_select: int = 5
    hand_table: Mapping[HandType, HandValue] = DEFAULT_HAND_TABLE

    def __post_init__(self) -> None:
        if self.hand_size < 1:
            raise ValueError("hand_size must be at least 1")
        if self.hands < 1:
            raise ValueError("hands must be at least 1")
        if self.discards < 0:
            raise ValueError("discards cannot be negative")
        if not 1 <= self.max_select <= 5:
            raise ValueError("max_select must be between 1 and 5")
        missing = set(HandType) - set(self.hand_table)
        if missing:
            names = ", ".join(sorted(h.label for h in missing))
            raise ValueError(f"hand_table is missing: {names}")
        
        # Make a read-only copy (MappingProxyType) of caller-supplied hand-table so that
        # changes to the original do not affect the Config hand table
        object.__setattr__(self, "hand_table", MappingProxyType(dict(self.hand_table)))

    def value(self, hand_type: HandType) -> HandValue:
        """Base chips and mult for a hand type."""
        return self.hand_table[hand_type]


DEFAULT_CONFIG = Config()
