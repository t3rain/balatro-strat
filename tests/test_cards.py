import pytest

from balatro_strat.cards import (
    ACE, CLUBS, DECK_SIZE, DIAMONDS, FULL_DECK, HEARTS, JACK, KING, QUEEN,
    SPADES, TEN, chips, hand_str, make_card, parse, parse_hand, rank, suit,
    to_str,
)


def test_deck_is_52_distinct_cards():
    assert len(FULL_DECK) == DECK_SIZE == 52
    assert len(set(FULL_DECK)) == 52


def test_every_rank_suit_pair_appears_once():
    pairs = {(rank(c), suit(c)) for c in FULL_DECK}
    assert pairs == {(r, s) for r in range(13) for s in range(4)}


@pytest.mark.parametrize("card", FULL_DECK)
def test_make_card_inverts_rank_and_suit(card):
    assert make_card(rank(card), suit(card)) == card


@pytest.mark.parametrize("card", FULL_DECK)
def test_string_round_trip(card):
    assert parse(to_str(card)) == card
    assert parse(to_str(card, symbols=False)) == card


@pytest.mark.parametrize(
    "text, chip_value",
    [("2s", 2), ("5h", 5), ("9d", 9), ("10c", 10),
     ("Js", 10), ("Qh", 10), ("Kd", 10), ("Ac", 11)],
)
def test_chip_values(text, chip_value):
    assert chips(parse(text)) == chip_value


def test_total_chips_in_deck():
    # 4 x (2+3+...+10) + 4 x (10+10+10) + 4 x 11 = 216 + 120 + 44
    assert sum(chips(c) for c in FULL_DECK) == 380


def test_named_rank_indices():
    assert rank(parse("10s")) == TEN
    assert rank(parse("Js")) == JACK
    assert rank(parse("Qs")) == QUEEN
    assert rank(parse("Ks")) == KING
    assert rank(parse("As")) == ACE


@pytest.mark.parametrize(
    "text, expected_suit",
    [("As", SPADES), ("A♠", SPADES), ("Ah", HEARTS), ("A♥", HEARTS),
     ("Ad", DIAMONDS), ("A♦", DIAMONDS), ("Ac", CLUBS), ("A♣", CLUBS)],
)
def test_suit_parsing(text, expected_suit):
    assert suit(parse(text)) == expected_suit


@pytest.mark.parametrize("text", ["as", "AS", " As ", "a♠"])
def test_parse_is_forgiving_about_case_and_spaces(text):
    assert parse(text) == make_card(ACE, SPADES)


def test_ten_has_two_spellings():
    assert parse("10h") == parse("Th") == parse("th")


@pytest.mark.parametrize("text", ["", "A", "1s", "11s", "Ax", "Zs", "10", "AsKs"])
def test_bad_input_raises(text):
    with pytest.raises(ValueError):
        parse(text)


@pytest.mark.parametrize("bad", [-1, 52, 100])
def test_out_of_range_card_raises(bad):
    with pytest.raises(ValueError):
        rank(bad)
    with pytest.raises(ValueError):
        chips(bad)


@pytest.mark.parametrize("r, s", [(-1, 0), (13, 0), (0, -1), (0, 4)])
def test_make_card_rejects_bad_indices(r, s):
    with pytest.raises(ValueError):
        make_card(r, s)


def test_parse_hand_and_display():
    hand = parse_hand("As 10h Td K♣ 2c")
    assert len(hand) == 5
    assert hand_str(hand) == "A♠ 10♥ 10♦ K♣ 2♣"
    assert hand_str(hand, symbols=False) == "As 10h 10d Kc 2c"


def test_parse_hand_allows_duplicates():
    # Test to check parse_hand allows duplicates
    assert parse_hand("As As") == (parse("As"), parse("As"))
