import tkinter as tk
from tkinter import messagebox
from typing import List

from domein import Game


class GameApp(tk.Tk):
    """Simple GUI to play the pyramid drinking game."""

    def __init__(self) -> None:
        super().__init__()
        self.title("DrankSpel")
        self.geometry("400x200")

        tk.Label(self, text="Spelers (comma-gescheiden):").pack(pady=5)
        self.players_entry = tk.Entry(self, width=40)
        self.players_entry.pack(pady=5)

        tk.Button(self, text="Start spel", command=self.start_game).pack(pady=5)
        tk.Button(self, text="Volgende kaart", command=self.next_card).pack(pady=5)

        self.card_label = tk.Label(self, text="", font=("Arial", 24))
        self.card_label.pack(pady=10)

        self.game: Game | None = None

    def start_game(self) -> None:
        names = [n.strip() for n in self.players_entry.get().split(",") if n.strip()]
        if not names:
            messagebox.showerror("Fout", "Voer minstens één speler in")
            return
        try:
            self.game = Game(names)
            self.card_label.config(text="")
        except ValueError as exc:  # invalid number of players
            messagebox.showerror("Fout", str(exc))

    def next_card(self) -> None:
        if not self.game:
            messagebox.showinfo("Info", "Start eerst een spel")
            return
        card = self.game.reveal_next_card()
        if card is None:
            messagebox.showinfo("Einde", "Piramide is op")
        else:
            self.card_label.config(text=card.rank)


def run() -> None:
    app = GameApp()
    app.mainloop()


if __name__ == "__main__":  # pragma: no cover - manual execution
    run()
