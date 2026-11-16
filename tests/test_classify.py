"""Tests for classify()."""

import itertools

import pytest

from balatro_strat.cards import parse_hand
from balatro_strat.config import HandType
from balatro_strat.scoring import classify


def check(played: str, expected_type: HandType, expected_scoring: str) -> None:
    """Classify played and compare against the expected type and scoring cards.
    Scoring cards are compared as sorted tuples, so the test doesn't depend on
    the order classify() returns them in.
    """
    hand_type, scoring = classify(parse_hand(played))
    assert hand_type == expected_type
    assert sorted(scoring) == sorted(parse_hand(expected_scoring))


# --------------- One case per hand type (5 cards played) ---------------

@pytest.mark.parametrize(
    "played, expected_type, expected_scoring",
    [
        ("Ks 9h 7d 4c 2s", HandType.HIGH_CARD, "Ks"),
        ("As Ah 9d 6c 2s", HandType.PAIR, "As Ah"),
        ("Js Jh 4d 4c 9s", HandType.TWO_PAIR, "Js Jh 4d 4c"),
        ("7s 7h 7d Kc 2s", HandType.THREE_OF_A_KIND, "7s 7h 7d"),
        ("5s 6h 7d 8c 9s", HandType.STRAIGHT, "5s 6h 7d 8c 9s"),
        ("2d 5d 8d Jd Kd", HandType.FLUSH, "2d 5d 8d Jd Kd"),
        ("8s 8h 8d 4c 4s", HandType.FULL_HOUSE, "8s 8h 8d 4c 4s"),
        ("Qs Qh Qd Qc 3s", HandType.FOUR_OF_A_KIND, "Qs Qh Qd Qc"),
        ("9c Tc Jc Qc Kc", HandType.STRAIGHT_FLUSH, "9c Tc Jc Qc Kc"),
    ],
)
def test_each_hand_type(played, expected_type, expected_scoring):
    check(played, expected_type, expected_scoring)


def test_rules_doc_examples():
    check("9s 9c 2h 2s 4c", HandType.TWO_PAIR, "9s 9c 2h 2s")
    check("Ks 7h 5d 3c 2s", HandType.HIGH_CARD, "Ks")
    check("As 2h 3d 4c 5s", HandType.STRAIGHT, "As 2h 3d 4c 5s")


# --------------- Fewer than 5 cards ---------------

@pytest.mark.parametrize(
    "played, expected_type, expected_scoring",
    [
        ("7h", HandType.HIGH_CARD, "7h"),
        ("7h 3c", HandType.HIGH_CARD, "7h"),
        ("As Ah", HandType.PAIR, "As Ah"),
        ("As Ah 3c", HandType.PAIR, "As Ah"),
        ("Js Jh 4d 4c", HandType.TWO_PAIR, "Js Jh 4d 4c"),
        ("7s 7h 7d", HandType.THREE_OF_A_KIND, "7s 7h 7d"),
        ("Qs Qh Qd Qc", HandType.FOUR_OF_A_KIND, "Qs Qh Qd Qc"),
    ],
)
def test_fewer_than_five_cards(played, expected_type, expected_scoring):
    check(played, expected_type, expected_scoring)


def test_four_suited_cards_is_not_a_flush():
    check("2h 6h 9h Kh", HandType.HIGH_CARD, "Kh")


def test_four_in_a_row_is_not_a_straight():
    check("5s 6h 7d 8c", HandType.HIGH_CARD, "8c")


def test_four_card_straight_flush_draw_is_nothing():
    check("5h 6h 7h 8h", HandType.HIGH_CARD, "8h")


def test_three_of_a_kind_plus_pair_needs_all_five_for_full_house():
    # Only 4 cards: three of a kind with a kicker, not a full house.
    check("8s 8h 8d 4c", HandType.THREE_OF_A_KIND, "8s 8h 8d")


# --------------- Straights and aces ---------------

def test_ace_low_straight():
    check("As 2h 3d 4c 5s", HandType.STRAIGHT, "As 2h 3d 4c 5s")


def test_ace_high_straight():
    check("Ts Jh Qd Kc As", HandType.STRAIGHT, "Ts Jh Qd Kc As")


def test_six_high_straight_above_the_wheel():
    check("2s 3h 4d 5c 6s", HandType.STRAIGHT, "2s 3h 4d 5c 6s")


@pytest.mark.parametrize("played", ["Qs Kh Ad 2c 3s", "Ks Ah 2d 3c 4s", "Js Qh Kd Ac 2s"])
def test_no_wraparound(played):
    hand_type, _ = classify(parse_hand(played))
    assert hand_type == HandType.HIGH_CARD


def test_gap_is_not_a_straight():
    check("5s 6h 7d 8c Ts", HandType.HIGH_CARD, "Ts")


@pytest.mark.parametrize(
    "played, expected_type, expected_scoring",
    [
        # Rank span of 4, but a pair inside: not a straight.
        ("5s 5h 6d 7c 9s", HandType.PAIR, "5s 5h"),
        ("9s 9h Td Jc Kd", HandType.PAIR, "9s 9h"),
        # Ace-low shape, but a pair inside: not a straight.
        ("2s 2h 3d 5c As", HandType.PAIR, "2s 2h"),
    ],
)
def test_straight_needs_five_distinct_ranks(played, expected_type, expected_scoring):
    check(played, expected_type, expected_scoring)


def test_ace_only_completes_a_straight_with_2_3_4_5():
    # 3-4-5-6-A: four in a row plus an ace is NOT a straight.
    check("3s 4h 5d 6c As", HandType.HIGH_CARD, "As")


def test_royal_flush_is_a_straight_flush():
    check("Th Jh Qh Kh Ah", HandType.STRAIGHT_FLUSH, "Th Jh Qh Kh Ah")


def test_ace_low_straight_flush():
    check("Ad 2d 3d 4d 5d", HandType.STRAIGHT_FLUSH, "Ad 2d 3d 4d 5d")


# --------------- Precedence and kickers ---------------

def test_full_house_beats_three_of_a_kind_and_pair():
    check("Ks Kh Kd 2c 2s", HandType.FULL_HOUSE, "Ks Kh Kd 2c 2s")


def test_four_of_a_kind_beats_full_house_reading():
    # 4 of one rank + 1 other: four of a kind, kicker excluded.
    check("3s 3h 3d 3c As", HandType.FOUR_OF_A_KIND, "3s 3h 3d 3c")


def test_straight_flush_beats_straight_and_flush():
    check("4s 5s 6s 7s 8s", HandType.STRAIGHT_FLUSH, "4s 5s 6s 7s 8s")


def test_flush_beats_straight_when_not_both():
    check("3c 7c 9c Jc Ac", HandType.FLUSH, "3c 7c 9c Jc Ac")


def test_high_card_scores_only_top_card_and_ace_is_top():
    check("As 9h 7d 4c 2s", HandType.HIGH_CARD, "As")


def test_two_pair_scores_both_pairs_not_kicker():
    check("2s 2h 3d 3c Ks", HandType.TWO_PAIR, "2s 2h 3d 3c")


def test_three_of_a_kind_with_two_different_kickers():
    check("9s 9h 9d 2c Ks", HandType.THREE_OF_A_KIND, "9s 9h 9d")


# --------------- Input order does not matter ---------------

@pytest.mark.parametrize(
    "played",
    ["8s 8h 8d 4c 4s", "As 2h 3d 4c 5s", "Js Jh 4d 4c 9s", "2d 5d 8d Jd Kd"],
)
def test_order_of_cards_does_not_matter(played):
    cards = parse_hand(played)
    expected_type, expected_scoring = classify(cards)
    for perm in itertools.permutations(cards):
        hand_type, scoring = classify(perm)
        assert hand_type == expected_type
        assert sorted(scoring) == sorted(expected_scoring)


def test_scoring_cards_are_a_subset_of_played_cards():
    cards = parse_hand("Qs Qh Qd Qc 3s")
    _, scoring = classify(cards)
    assert set(scoring) <= set(cards)


# --------------- Invalid input ---------------

@pytest.mark.parametrize("played", ["", "As Ks Qs Js Ts 9s"])
def test_wrong_number_of_cards_raises(played):
    with pytest.raises(ValueError):
        classify(parse_hand(played))


# --------------- Modified decks: duplicate cards ---------------

def test_five_of_a_kind():
    check("9s 9h 9d 9c 9s", HandType.FIVE_OF_A_KIND, "9s 9h 9d 9c 9s")


def test_flush_house():
    check("Kh Kh Kh 7h 7h", HandType.FLUSH_HOUSE, "Kh Kh Kh 7h 7h")


def test_flush_five():
    check("As As As As As", HandType.FLUSH_FIVE, "As As As As As")


def test_flush_with_a_pair_is_a_flush():
    # Only possible with duplicates: a pair inside a flush. Flush ranks above pair.
    check("4d 4d 8d Jd Kd", HandType.FLUSH, "4d 4d 8d Jd Kd")
