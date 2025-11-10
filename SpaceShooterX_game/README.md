# Space Shooter (Python)

A compact 2D arcade-style space shooter written in Python using pygame.

Features
- Levels: every 10 points increases enemy speed and tightens spawn timing
- Health: player starts with 3 lives; an enemy that crosses the bottom costs a life
- Power-ups: destroyed enemies sometimes drop stars that upgrade your weapon (up to 3 levels)
- High score: saved to `highscore.json` in the project folder (JSON)
- Background music & simple SFX: auto-generated WAVs if not present
- Start menu, pause (P), and game over screen

Requirements
- Python 3.8+
- pygame

Install
In PowerShell (Windows):

```powershell
python -m pip install -r requirements.txt
```

Run

```powershell
python main.py
```

Controls
- Left / Right arrows or A / D: Move
- Space: Shoot
- P: Pause / Unpause
- Enter: Start or restart from menus

Notes
- The game will generate small WAV files (`bgm.wav`, `snd_shoot.wav`, `snd_explode.wav`) in the project folder if they are missing.
- High score is persisted across runs in `highscore.json`.

Suggestions
- Add your own art/sounds by replacing the generated WAVs and customizing drawing code in `main.py`.
- Tweak difficulty, spawn rates, and power-up probabilities in `main.py` constants.

Have fun!"