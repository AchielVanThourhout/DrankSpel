from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from domein import Card, Game
from persistentie import load_game, save_game


def test_pyramid_setup():
    game = Game(["A", "B", "C"])
    assert len(game.players) == 3
    assert all(len(p.hand) == 4 for p in game.players)
    # For 3 players, the pyramid should have 8 rows and 4 rest cards
    assert len(game.pyramid.rows) == 8
    assert len(game.rest_stapel) == 4


def test_play_turn_outcomes():
    game = Game(["A", "B"])

    claimer = game.players[0]
    target = game.players[1]

    # target believes -> target drinks 1
    next_card = game.pyramid.rows[0][0]
    claimer.hand[0] = next_card
    _, outcome = game.play_turn(claimer, target, 0, True)
    assert target.drinks_taken == 1
    assert "drinkt 1" in outcome

    # challenge is correct -> target drinks 2
    next_card = game.pyramid.rows[0][1]
    claimer.hand[1] = next_card
    _, outcome = game.play_turn(claimer, target, 1, False)
    assert target.drinks_taken == 3
    assert "drinkt 2" in outcome

    # challenge fails -> claimer drinks 2
    next_card = game.pyramid.rows[0][2]
    mismatch = Card("A" if next_card.rank != "A" else "2", next_card.suit)
    claimer.hand[2] = mismatch
    _, outcome = game.play_turn(claimer, target, 2, False)
    assert claimer.drinks_taken == 2
    assert "drinkt 2" in outcome


def test_persistence_round_trip(tmp_path: Path):
    game = Game(["A", "B"])
    expected = game.pyramid.rows[0][0]
    save_file = tmp_path / "game.json"
    save_game(game, save_file)
    loaded = load_game(save_file)
    # Next card after load should match the peeked card
    assert loaded.reveal_next_card().rank == expected.rank
    assert [p.name for p in loaded.players] == ["A", "B"]
