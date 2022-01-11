# wwyd-bot
Node.js Discord bot for riichi mahjong "what would you discard"-style questions.
Currently uses python and Pillow for generating game state pictures.

## To-do
### Now
- finish game state generation code (current priority)
- rich discord integration
- autoplay (new problem posted to channel every so often)
- support for game-agnostic wwyd questions

### Later
- find a easier way to generate new problems (see notes)
- try to port image processing to node
- descriptions for why certain discards are better than others

## Notes
For the sample problem, the best discards are determined using critter's akochan in conjunction with Equim-chan's akochan-reviewer.
This isn't a requirement for creating problems.
However, the only other alternatives are either being good at mahjong (which I'm not) and creating them yourself, or taking them from another source.
I'm not too inclined to use any of these options, so the only problem provided with this repo is the sample problem.
