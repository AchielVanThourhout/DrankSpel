"""Persist and restore game state using JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from domein import Card, Game, Pyramid


def _card_to_tuple(card: Card) -> tuple[str, str]:
    return card.rank, card.suit


def _card_from_tuple(data: List[str]) -> Card:
    rank, suit = data
    return Card(rank, suit)


def save_game(game: Game, filename: str | Path) -> None:
    """Serialize the current game state to *filename*."""
    data: Dict[str, Any] = {
        "players": [
            {
                "name": p.name,
                "hand": [_card_to_tuple(c) for c in p.hand],
                "revealed": list(p.revealed_indices),
                "drinks_taken": p.drinks_taken,
            }
            for p in game.players
        ],
        "pyramid": {
            "rows": [[_card_to_tuple(c) for c in row] for row in game.pyramid.rows],
            "pos": {"row": game.pyramid._row, "col": game.pyramid._col},
        },
        "rest_stapel": [_card_to_tuple(c) for c in game.rest_stapel],
    }
    Path(filename).write_text(json.dumps(data), encoding="utf-8")


def load_game(filename: str | Path) -> Game:
    """Load a game previously stored with :func:`save_game`."""
    data = json.loads(Path(filename).read_text(encoding="utf-8"))
    names = [p["name"] for p in data["players"]]
    game = Game(names)

    for p_data, player in zip(data["players"], game.players):
        player.hand = [_card_from_tuple(t) for t in p_data["hand"]]
        player.revealed_indices = set(p_data["revealed"])
        player.drinks_taken = p_data["drinks_taken"]

    rows_data = data["pyramid"]["rows"]
    cards = [_card_from_tuple(t) for row in rows_data for t in row]
    rows = len(rows_data)
    game.pyramid = Pyramid(cards, rows)
    game.pyramid.rows = [[_card_from_tuple(t) for t in row] for row in rows_data]
    game.pyramid._row = data["pyramid"]["pos"]["row"]
    game.pyramid._col = data["pyramid"]["pos"]["col"]

    game.rest_stapel = [_card_from_tuple(t) for t in data["rest_stapel"]]
    return game
