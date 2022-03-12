# wwyd-bot
Node.js Discord bot for riichi mahjong "what would you discard"-style questions.
Uses akochan with akochan-reviewer to generate questions.
Uses discord.js for discord integration.
Uses python and Pillow for generating game state pictures.

## Features
 - Pictures are quickly generated when a problem is requested, no need to cache
 - Can generate random problems given akochan-reviewer json log output using generateTempWWYDProblem.py (place game logs into games/)
 - Particularly interesting problems can be cached by running createGameStateFromAkochan.py (place output into akochans/)

## To use
 - !akochan to pull a random question from akochans/
 - !test to pull a random question generated from game logs in games/

## Planned features
 - Timer system (post new question every X hours)
 - Currency / ranking system
 - Deploy as webpage
