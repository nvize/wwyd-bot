const { Client, Intents } = require('discord.js');
const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });
const config = require('./config.json');

// When the client is ready, run this code (only once)
client.once('ready', () => {
	console.log('Ready!');
});

client.on("messageCreate", async (message) => {
     if (message.author.bot) return false; 
    if (message.content.toLowerCase() == "!akochan") {
        let user = message.author;
        let game = require("./akochans/akochan-1.json");
        message.reply(`Puzzle name: ${game.name}\n`
            + `You are ${game.seat}.\n`
            + `East discards: ${game.eastDiscards}, East calls: ${game.eastCalls}\n`
            + `South discards: ${game.southDiscards}, South calls: ${game.southCalls}\n` 
            + `West discards: ${game.westDiscards}, West calls: ${game.westCalls}\n` 
            + `North discards: ${game.northDiscards}, North calls: ${game.northCalls}\n` 
            + `Your hand: ${game.hand}, Dora indicator: ${game.doraInd}\n` 
            + `WWYD? You have 30 seconds to answer!`);
        let filter = m => m.author === user;
        let answer = await message.channel.awaitMessages({filter, max: 1, time: 30_000});
        if(answer.size < 1) {
            message.reply(`Times up!.\n`
                + `The best discards were: ${game.bestDiscards}\n`
                + `Their EVs were: ${game.evs}`);
      } else {
            answer.first().reply(`You said ${answer.first()}.\n`
                + `The best discards were: ${game.bestDiscards}\n`
                + `Their EVs were: ${game.evs}`);
      }
  }
  console.log(`Message from ${message.author.username}: ${message.content}`);
});

client.login(config.token);