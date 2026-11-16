"""Hand classification and scoring.
"""
from collections.abc import Sequence
from collections import Counter
from balatro_strat.cards import Card
from balatro_strat.config import HandType

from balatro_strat.cards import rank, suit

def classify(cards: Sequence[Card]) -> tuple[HandType, tuple[Card, ...]]:
    """Classify a played hand.
    The return is the Hand type and the scoring cards.
    """

    if not 1 <= len(cards) <= 5:
        raise ValueError(f"number of cards played invalid: {len(cards)}")

    rank_frequency = Counter([rank(card) for card in cards]).most_common()
    suit_frequency = Counter([suit(card) for card in cards]).most_common()
    ranks = sorted([rank(card) for card in cards])

    flush = False
    straight = False
    five_of_a_kind = False
    four_of_a_kind = False
    full_house = False
    three_of_a_kind = False
    two_pair = False
    pair = False

    if suit_frequency[0][1] == 5:
        flush = True

    if len(set(ranks)) == 5:
        if ranks[4] - ranks[0] == 4 or ranks == [0, 1, 2, 3, 12]:
            straight = True

    if rank_frequency[0][1] == 5 :
        five_of_a_kind = True
    elif rank_frequency[0][1] == 4:
        four_of_a_kind = True
        top_rank = rank_frequency[0][0]
        scoring = tuple(c for c in cards if rank(c) == top_rank)
    elif rank_frequency[0][1] == 3:
        if len(rank_frequency) > 1 and rank_frequency[1][1] == 2:
            full_house = True
        else:
            three_of_a_kind = True
            top_rank = rank_frequency[0][0]
            scoring = tuple(c for c in cards if rank(c) == top_rank)
    elif rank_frequency[0][1] == 2:
        if len(rank_frequency) > 1 and rank_frequency[1][1] == 2:
            two_pair = True
            top_ranks = {r for r, n in rank_frequency if n == 2}
            scoring = tuple(c for c in cards if rank(c) in top_ranks)
        else:
            pair = True  
            top_rank = rank_frequency[0][0]
            scoring = tuple(c for c in cards if rank(c) == top_rank)  

    if flush and five_of_a_kind:
        return HandType.FLUSH_FIVE, tuple(cards)
    elif flush and full_house:
        return HandType.FLUSH_HOUSE, tuple(cards)
    elif five_of_a_kind:
        return HandType.FIVE_OF_A_KIND, tuple(cards)
    elif straight and flush:
        return HandType.STRAIGHT_FLUSH, tuple(cards)
    elif four_of_a_kind:
        return HandType.FOUR_OF_A_KIND, scoring
    elif full_house:
        return HandType.FULL_HOUSE, tuple(cards)
    elif flush:
        return HandType.FLUSH, tuple(cards)
    elif straight:
        return HandType.STRAIGHT, tuple(cards)
    elif three_of_a_kind:
        return HandType.THREE_OF_A_KIND, scoring
    elif two_pair:
        return HandType.TWO_PAIR, scoring
    elif pair:
        return HandType.PAIR, scoring
    else:
        top_rank = ranks[-1]
        return HandType.HIGH_CARD, tuple(card for card in cards if rank(card) == top_rank)
