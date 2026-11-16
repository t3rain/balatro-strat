"""Card encoding.

Every card is an int in 0...51. We use rank major encoding from here on. Later on, count matrices
will also be easier to handle (row = rank, column = suit)

    card = rank * 4 + suit

    rank: 0..12  ->  2 3 4 5 6 7 8 9 10 J Q K A
    suit: 0..3   ->  spades, hearts, clubs, diamonds

Plain ints are hashable, fast to compare, and map directly onto a 13x4 count
matrix (row = rank, column = suit), which is what the exact solver will use.
"""
from collections.abc import Iterable

Card = int

NUM_RANKS = 13
NUM_SUITS = 4
DECK_SIZE = NUM_RANKS * NUM_SUITS

# named indices, for the other cards, this is just (value-2)
TEN, JACK, QUEEN, KING, ACE = 8, 9, 10, 11, 12

SPADES, HEARTS, CLUBS, DIAMONDS = 0, 1, 2, 3

RANK_CHARS = "23456789TJQKA"   # canonical one-char parse form ("T" = ten)
RANK_NAMES = ("2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A")
SUIT_CHARS = "shcd"            # ASCII form
SUIT_SYMBOLS = "♠♥♣♦"          # display form

FULL_DECK: tuple[Card, ...] = tuple(range(DECK_SIZE))


def make_card(rank: int, suit: int) -> Card:
    """Build a card from a rank and suit index."""
    if not 0 <= rank < NUM_RANKS:
        raise ValueError(f"rank index out of range: {rank}")
    if not 0 <= suit < NUM_SUITS:
        raise ValueError(f"suit index out of range: {suit}")
    return rank * NUM_SUITS + suit


def _check(card: Card) -> None:
    if not 0 <= card < DECK_SIZE:
        raise ValueError(f"card out of range: {card}")


def rank(card: Card) -> int:
    """Return rank index."""
    _check(card)
    return card // NUM_SUITS


def suit(card: Card) -> int:
    """Return suit index."""
    _check(card)
    return card % NUM_SUITS


def chips(card: Card) -> int:
    """Chip value when the card scores: 2-10 face value, J/Q/K 10, A 11.
    An ace is always worth 11, no matter lower or higher.
    """
    r = rank(card)
    if r == ACE:
        return 11
    if r >= TEN:
        return 10
    return r + 2


def parse(text: str) -> Card:
    """Parse one card.
    First character should be 2..10, "T", "J", "Q", "K" or "A" in any case
    Second character can be a letter ("s", "h", "c", "d" in any case) or a symbol ("♠", "♥", "♦", "♣")
    Examples: "As", "10h", "Td", "K♣".
    """
    t = text.strip()
    if len(t) < 2:
        raise ValueError(f"cannot parse card: {text!r}")
    rank_part, suit_part = t[:-1].upper(), t[-1]

    # only in this case the rank_part will have 2 chars
    if rank_part == "10":   
        rank_part = "T"
    if len(rank_part) != 1 or rank_part not in RANK_CHARS:
        raise ValueError(f"unknown rank in card: {text!r}")

    if suit_part in SUIT_SYMBOLS:
        s = SUIT_SYMBOLS.index(suit_part)
    elif suit_part.lower() in SUIT_CHARS:
        s = SUIT_CHARS.index(suit_part.lower())
    else:
        raise ValueError(f"unknown suit in card: {text!r}")

    return make_card(RANK_CHARS.index(rank_part), s)


def parse_hand(text: str) -> tuple[Card, ...]:
    """Parse whitespace-separated cards, e.g. "As Kh 10d 9c 2s"."""
    return tuple(parse(tok) for tok in text.split())


def to_str(card: Card, symbols: bool = True) -> str:
    """Display form: "A♠" (default) or "As" with symbols=False."""
    suits = SUIT_SYMBOLS if symbols else SUIT_CHARS
    return RANK_NAMES[rank(card)] + suits[suit(card)]


def hand_str(cards: Iterable[Card], symbols: bool = True) -> str:
    """Display a sequence of cards, e.g. "A♠ K♥ 10♦"."""
    return " ".join(to_str(c, symbols) for c in cards)
