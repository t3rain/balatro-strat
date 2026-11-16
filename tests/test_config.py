import pytest
from types import MappingProxyType

from balatro_strat.config import (
    ANTE1_TARGETS, DEFAULT_CONFIG, DEFAULT_HAND_TABLE, DUPLICATE_ONLY_HANDS,
    Config, HandType, HandValue,
)

# Ensure consistency with config
RULES_TABLE = {
    HandType.HIGH_CARD: (5, 1),
    HandType.PAIR: (10, 2),
    HandType.TWO_PAIR: (20, 2),
    HandType.THREE_OF_A_KIND: (30, 3),
    HandType.STRAIGHT: (30, 4),
    HandType.FLUSH: (35, 4),
    HandType.FULL_HOUSE: (40, 4),
    HandType.FOUR_OF_A_KIND: (60, 7),
    HandType.STRAIGHT_FLUSH: (100, 8),
    HandType.FIVE_OF_A_KIND: (120, 12),
    HandType.FLUSH_HOUSE: (140, 14),
    HandType.FLUSH_FIVE: (160, 16),
}


def test_table_matches_rules_doc():
    assert set(DEFAULT_HAND_TABLE) == set(HandType)
    for hand_type, (base_chips, mult) in RULES_TABLE.items():
        assert DEFAULT_HAND_TABLE[hand_type] == HandValue(base_chips, mult), hand_type


def test_poker_order():
    order = [
        "HIGH_CARD", "PAIR", "TWO_PAIR", "THREE_OF_A_KIND", "STRAIGHT", "FLUSH",
        "FULL_HOUSE", "FOUR_OF_A_KIND", "STRAIGHT_FLUSH", "FIVE_OF_A_KIND",
        "FLUSH_HOUSE", "FLUSH_FIVE",
    ]
    assert [h.name for h in sorted(HandType)] == order


def test_level_one_base_score_never_decreases_with_hand_strength():
    # Level one score table scores is sorted in poker order
    base = [DEFAULT_HAND_TABLE[h].chips * DEFAULT_HAND_TABLE[h].mult for h in sorted(HandType)]
    assert base == sorted(base)


def test_duplicate_only_hands():
    assert DUPLICATE_ONLY_HANDS == {
        HandType.FIVE_OF_A_KIND, HandType.FLUSH_HOUSE, HandType.FLUSH_FIVE,
    }


def test_labels():
    assert HandType.THREE_OF_A_KIND.label == "Three of a Kind"
    assert HandType.FIVE_OF_A_KIND.label == "Five of a Kind"
    assert HandType.STRAIGHT_FLUSH.label == "Straight Flush"


def test_default_config_is_vanilla():
    cfg = DEFAULT_CONFIG
    assert (cfg.hand_size, cfg.hands, cfg.discards, cfg.max_select) == (8, 4, 3, 5)
    assert cfg.value(HandType.FLUSH) == HandValue(35, 4)
    assert ANTE1_TARGETS == (300, 450, 600)


def test_config_is_immutable():
    with pytest.raises(AttributeError):
        DEFAULT_CONFIG.hands = 10
    with pytest.raises(TypeError):
        DEFAULT_CONFIG.hand_table[HandType.FLUSH] = HandValue(1000, 100)


def test_custom_table_is_frozen_copy():
    table = dict(DEFAULT_HAND_TABLE)
    cfg = Config(hand_table=table)
    table[HandType.FLUSH] = HandValue(1000, 100)   # mutate the caller's dict...
    assert cfg.value(HandType.FLUSH) == HandValue(35, 4)   # ...config is unaffected


def test_proxy_input_is_copied():
    table = dict(DEFAULT_HAND_TABLE)
    cfg = Config(hand_table=MappingProxyType(table))
    table[HandType.FLUSH] = HandValue(1000, 100)
    assert cfg.value(HandType.FLUSH) == HandValue(35, 4)


def test_levelled_table_is_allowed():
    table = dict(DEFAULT_HAND_TABLE)
    table[HandType.FLUSH] = HandValue(50, 6)   # flush at level 2
    assert Config(hand_table=table).value(HandType.FLUSH) == HandValue(50, 6)


@pytest.mark.parametrize(
    "kwargs",
    [{"hand_size": 0}, {"hands": 0}, {"discards": -1},
     {"max_select": 0}, {"max_select": 6}],
)
def test_invalid_config_raises(kwargs):
    with pytest.raises(ValueError):
        Config(**kwargs)

# incomplete scoring table raises ValueError
# with a string of missing hands
def test_incomplete_table_raises():
    table = dict(DEFAULT_HAND_TABLE)
    del table[HandType.PAIR]
    with pytest.raises(ValueError, match="Pair"):
        Config(hand_table=table)


@pytest.mark.parametrize("chips, mult", [(-1, 1), (10, 0)])
def test_invalid_hand_value_raises(chips, mult):
    with pytest.raises(ValueError):
        HandValue(chips, mult)
