"""Simple console interface to play the pyramid drinking game."""
from __future__ import annotations

from typing import List, Optional

from domein import Game, Player


def _get_player(game: Game, name: str) -> Optional[Player]:
    for player in game.players:
        if player.name == name:
            return player
    return None


def _ask_players() -> List[str]:
    names = input("Spelers (comma-gescheiden): ")
    return [n.strip() for n in names.split(",") if n.strip()]


def run() -> None:
    """Start an interactive session of the game."""
    player_names = _ask_players()
    game = Game(player_names)

    while True:
        card = game.reveal_next_card()
        if card is None:
            print("Piramide is op. Spel voorbij!")
            break
        print(f"Piramidekaart: {card.rank}")

        claimer_name = input("Claimer (enter voor geen claim): ").strip()
        if not claimer_name:
            continue
        claimer = _get_player(game, claimer_name)
        if claimer is None:
            print("Onbekende speler")
            continue

        target_name = input("Doelwit: ").strip()
        target = _get_player(game, target_name)
        if target is None or target is claimer:
            print("Ongeldig doelwit")
            continue

        try:
            index = int(input("Welke kaartindex (0-3): "))
        except ValueError:
            print("Ongeldige index")
            continue

        believes = input("Gelooft doelwit? (j/n): ").strip().lower() != "n"
        _, outcome = game.play_turn(claimer, target, index, believes)
        if outcome:
            print(outcome)


if __name__ == "__main__":  # pragma: no cover - manual execution
    run()
