"""Domain classes for the DrankSpel application.

The module implements the core logic for preparing a game of the
pyramid drinking game and for processing a single turn.  It follows the
requirements described in the user stories:

* Shuffle a standard deck and deal four cards to each player.
* Build the largest possible pyramid from the remaining cards.
* Allow players to claim that they hold the same rank as the revealed
  pyramid card and handle challenges.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Card and deck utilities
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Card:
    """Representation of a playing card.

    Only the rank matters for the game logic, the suit is retained for
    completeness.
    """

    rank: str
    suit: str

    def __str__(self) -> str:  # pragma: no cover - tiny helper
        return f"{self.rank} of {self.suit}"


class Deck:
    """A standard deck of 52 playing cards."""

    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suits = ["hearts", "diamonds", "clubs", "spades"]

    def __init__(self) -> None:
        self.cards: List[Card] = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
        if len(self.cards) != 52:
            raise ValueError("Deck must contain 52 cards")

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self, n: int) -> List[Card]:
        """Remove *n* cards from the top of the deck and return them."""
        if n > len(self.cards):
            raise ValueError("Not enough cards to deal")
        dealt = self.cards[:n]
        del self.cards[:n]
        return dealt

    def __len__(self) -> int:  # pragma: no cover - small helper
        return len(self.cards)


# ---------------------------------------------------------------------------
# Player and pyramid structures
# ---------------------------------------------------------------------------


class Player:
    """A player participating in the game."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.hand: List[Card] = []
        self.revealed_indices: set[int] = set()
        self.drinks_taken = 0

    # -- hand management -------------------------------------------------
    def receive(self, cards: List[Card]) -> None:
        self.hand.extend(cards)

    def reveal(self, index: int) -> Card:
        """Reveal the card at *index* and return it."""
        self.revealed_indices.add(index)
        return self.hand[index]

    # -- drink tracking --------------------------------------------------
    def drink(self, amount: int) -> None:
        self.drinks_taken += amount


class Pyramid:
    """Structure holding the pyramid of face-down cards.

    Rows are stored from bottom to top.  :meth:`next_card` returns the
    next card in play, iterating from the bottom row left-to-right and
    row-by-row towards the top.
    """

    def __init__(self, cards: List[Card], rows: int) -> None:
        self.rows: List[List[Card]] = []
        idx = 0
        for size in range(rows, 0, -1):
            self.rows.append(cards[idx : idx + size])
            idx += size
        self._row = 0
        self._col = 0

    def next_card(self) -> Optional[Card]:
        if self._row >= len(self.rows):
            return None
        card = self.rows[self._row][self._col]
        self._col += 1
        if self._col >= len(self.rows[self._row]):
            self._row += 1
            self._col = 0
        return card


# ---------------------------------------------------------------------------
# Game logic
# ---------------------------------------------------------------------------


class Game:
    """Encapsulates the state and rules of the pyramid drinking game."""

    def __init__(self, player_names: List[str]):
        if not 2 <= len(player_names) <= 12:
            raise ValueError("minstens 2, max 12 spelers voor 4 kaarten pp")

        self.players = [Player(name) for name in player_names]
        self.deck = Deck()
        self.deck.shuffle()

        # deal four cards per player
        for player in self.players:
            player.receive(self.deck.deal(4))

        # build pyramid from remaining cards
        remaining = len(self.deck)
        rows = self._max_pyramid_rows(remaining)
        pyramid_cards = self.deck.deal(rows * (rows + 1) // 2)
        self.pyramid = Pyramid(pyramid_cards, rows)

        # leftover cards become the rest stack
        self.rest_stapel = self.deck.deal(len(self.deck))

    @staticmethod
    def _max_pyramid_rows(remaining: int) -> int:
        """Return the largest *n* for which ``n(n+1)/2 <= remaining``."""
        return (math.isqrt(8 * remaining + 1) - 1) // 2

    def reveal_next_card(self) -> Optional[Card]:
        """Reveal the next card in the pyramid."""
        return self.pyramid.next_card()

    # -- turn handling ---------------------------------------------------
    def play_turn(
        self,
        claimer: Optional[Player],
        target: Optional[Player],
        chosen_index: Optional[int],
        target_believes: bool = True,
    ) -> Tuple[Card, Optional[str]]:
        """Process a single turn.

        Parameters mirror the steps from the use case.  The next pyramid
        card is revealed.  If no claim is made (``claimer`` or ``target``
        is ``None``) the method returns immediately.  Otherwise, the
        challenge logic is executed and a short description of the
        outcome is returned.
        """

        card = self.reveal_next_card()
        if card is None:
            raise RuntimeError("No more cards in the pyramid")

        outcome: Optional[str] = None
        if claimer is None or target is None or chosen_index is None:
            return card, outcome

        if target_believes:
            target.drink(1)
            outcome = f"{target.name} drinkt 1"
        else:
            shown = claimer.reveal(chosen_index)
            if shown.rank == card.rank:
                target.drink(2)
                outcome = f"{target.name} drinkt 2"
            else:
                claimer.drink(2)
                outcome = f"{claimer.name} drinkt 2"
        return card, outcome
