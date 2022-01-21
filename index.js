const { Client, Intents } = require('discord.js');
const Discord = require('discord.js');
const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });
const config = require('./config.json');
const spawn = require("child_process").spawn;
const fs = require('fs');

const akochanProblems = fs.readdirSync('./akochans');

// When the client is ready, run this code (only once)
client.once('ready', () => {
    console.log('Ready!');
});

client.on("messageCreate", async (message) => {
    if (message.author.bot) return false;
    if (message.content.toLowerCase() == "!akochan") {
        let user = message.author;
        let gameFilepath = `./akochans/${akochanProblems[Math.floor(Math.random() * akochanProblems.length)]}`;
        let game = require(gameFilepath);
        let gameImageBase64 = '';
        let pythonProcess = spawn('py', ["./createGameStatePicture.py", gameFilepath]);
        pythonProcess.stdout.on('data', (data) => {
            gameImageBase64 += data;
        });
        pythonProcess.on('close', function (code) {
            whateves(gameImageBase64);
            console.log('done!');
        });

        async function whateves(gameImageBase64) {
            let sfbuff = new Buffer.from(gameImageBase64, 'base64');
            await message.reply({ content: `Puzzle name: ${game.name}. You are ${game.seat}. Dora indicator: ${game.doraInd}. WWYD? You have 30 seconds to answer!`, files: [{ attachment: sfbuff }] });
            let filter = m => m.author === user;
            let answer = await message.channel.awaitMessages({ filter, max: 1, time: 30_000 });
            if (answer.size < 1) {
                message.reply(`Times up!.\n`
                    + `The best discards were: ${game.bestDiscards}\n`
                    + `Their EVs were: ${game.evs}`);
            } else {
                let ranking = game.bestDiscards.indexOf(answer.first().content);
                console.log(answer.first().content);
                console.log(ranking);
                let responseIntro = `You said ${answer.first().content}. `;
                if (ranking > -1) {
                    if (ranking === 0) {
                        responseIntro = responseIntro + `That was the best discard! You earned 5 akocoins!`;
                    } else if (ranking === 4) {
                        responseIntro = responseIntro + `That was the number 5 discard! You earned 1 akocoin!`;
                    } else {
                        responseIntro = responseIntro + `That was the number ${ranking + 1} discard! You earned ${5 - ranking} akocoins!`;
                    }
                }
                answer.first().reply(`${responseIntro}\n`
                    + `The best discards were: ${game.bestDiscards}\n`
                    + `Their EVs were: ${game.evs}`);
            }
        }
    }
});

client.login(config.token);