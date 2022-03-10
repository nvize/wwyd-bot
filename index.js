const { Client, Intents } = require('discord.js');
const Discord = require('discord.js');
const { MessageActionRow, MessageButton } = require('discord.js');
const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });
const config = require('./config.json');
const spawn = require("child_process").spawn;
const fs = require('fs');
const mongo = require('./mongo.js')
const mongoose = require('mongoose')

const akochanProblems = fs.readdirSync('./akochans');
const gameLogs = fs.readdirSync('./games');

// When the client is ready, run this code (only once)
client.once('ready', async () => {
    console.log('Ready!');

    await mongo().then((mongoose) => {
        try {
            console.log('connected to mongo')
        } catch {
            console.log(error)
        }
    })
});

client.on("messageCreate", async (message) => {
    if (message.author.bot) return false;
    if (message.content.toLowerCase() == "!akochan") {
        let user = message.author;
        let gameFilepath = `./akochans/${akochanProblems[Math.floor(Math.random() * akochanProblems.length)]}`;
        let game = require(gameFilepath);
        let gameImageBase64 = '';
        let pythonProcess = spawn('py', ["./createGameStatePicture.py", gameFilepath, "filepath"])
        pythonProcess.stdout.on('data', (data) => {
            gameImageBase64 += data;
        });
        pythonProcess.on('close', function (code) {
            whateves(gameImageBase64);
            console.log('done!');
        });

        async function whateves(gameImageBase64) {
            let sfbuff = new Buffer.from(gameImageBase64, 'base64');
            let rows = [];
            for (let x in game.potentialDiscards) {
                if (x % 5 == 0)
                    rows.push(new MessageActionRow())
                rows[Math.floor(x/5)].addComponents(
                    new MessageButton()
					.setCustomId(x)
					.setLabel(game.potentialDiscards[x])
					.setStyle('PRIMARY')
                );
            }
            //let actionRows = [rows[0], rows[1]];
            let problemReply = await message.reply({ content: `Puzzle name: ${game.name}. You are ${game.seat}. Dora indicator: ${game.doraInd}. WWYD? You have 30 seconds to answer!`, files: [{ attachment: sfbuff }], components:rows });
            const filter = i => {
                i.deferUpdate();
                return i.user === user;
            };
            let answer = await message.channel.awaitMessageComponent({ filter, componentType: 'BUTTON', max: 1, time: 30_000 })
                .catch(err => console.log(`No interactions were collected.`));
            rows.forEach(row => row.components.forEach(button => button.setDisabled(true)))
            //actionRows = [rows[0], rows[1]];
            problemReply.edit({ content: `Puzzle name: ${game.name}. You are ${game.seat}. Dora indicator: ${game.doraInd}. WWYD? You have 30 seconds to answer!`, files: [{ attachment: sfbuff }], components:rows });
            if (answer == null) {
                message.reply(`Times up!.\n`
                    + `The best discards were: ${game.bestDiscards}\n`
                    + `Their EVs were: ${game.evs}`);
            } else {
                let ranking = game.bestDiscards.indexOf(answer.component.label);
                console.log(answer.component.label);
                console.log(ranking);
                let responseIntro = `You said ${answer.component.label}. `;
                if (ranking > -1) {
                    if (ranking === 0) {
                        responseIntro = responseIntro + `That was the best discard! You earned 5 akocoins!`;
                    } else if (ranking === 4) {
                        responseIntro = responseIntro + `That was the number 5 discard! You earned 1 akocoin!`;
                    } else {
                        responseIntro = responseIntro + `That was the number ${ranking + 1} discard! You earned ${5 - ranking} akocoins!`;
                    }
                }
                message.reply(`${responseIntro}\n`
                    + `The best discards were: ${game.bestDiscards}\n`
                    + `Their EVs were: ${game.evs}`);
            }            
        }
    } else if (message.content.toLowerCase() == "!test") {
        let user = message.author;
        //let filePath = `./games/${gameLogs[Math.floor(Math.random() * gameLogs.length)]}`;
        let filePath = `./games/3_3_2022_Gold_Room_South.json`
        let rawFileData = fs.readFileSync(filePath);
        let fileData = JSON.parse(rawFileData)
        let numOfRounds = Object.keys(fileData.kyokus).length - 1;
        let round = Math.floor(Math.random() * numOfRounds);
        let numOfTurns = fileData.kyokus[round].entries[fileData.kyokus[round].entries.length - 1].junme;
        let turn =  6 + Math.floor(Math.random() * (numOfTurns - 6));
        console.log(String(round))
        console.log(String(turn))
        let pythonProcess = spawn('py', ["./generateRandomWWYDProblem.py", filePath, round, turn])
        let gameImageBase64 = '';
        pythonProcess.stdout.on('data', (data) => {
            gameImageBase64 += data;
        });
        pythonProcess.on('close', function (code) {
            whateves(gameImageBase64);
        });

        async function whateves(gameImageBase64) {
            let gamefile = fs.readFileSync("./randWWYD.json");
            let game2 = JSON.parse(gamefile)
            let sfbuff = new Buffer.from(gameImageBase64, 'base64');
            let rows = [];
            for (let x in game2.potentialDiscards) {
                if (x % 5 == 0)
                    rows.push(new MessageActionRow())
                rows[Math.floor(x/5)].addComponents(
                    new MessageButton()
					.setCustomId(x)
					.setLabel(game2.potentialDiscards[x])
					.setStyle('PRIMARY')
                );
            }
            //let actionRows = [rows[0], rows[1]];
            let problemReply = await message.reply({ content: `${filePath}. Round: ${round}. Turn: ${turn}. Puzzle name: ${game2.name}. You are ${game2.seat}. Dora indicator: ${game2.doraInd}. WWYD? You have 30 seconds to answer!`, files: [{ attachment: sfbuff }], components:rows });
            const filter = i => {
                i.deferUpdate();
                return i.user === user;
            };
            let answer = await message.channel.awaitMessageComponent({ filter, componentType: 'BUTTON', max: 1, time: 30_000 })
                .catch(err => console.log(`No interactions were collected.`));
            rows.forEach(row => row.components.forEach(button => button.setDisabled(true)))
            //actionRows = [rows[0], rows[1]];
            problemReply.edit({ content: `${filePath}. Round: ${round}. Turn: ${turn}. Puzzle name: ${game2.name}. You are ${game2.seat}. Dora indicator: ${game2.doraInd}. WWYD? You have 30 seconds to answer!`, files: [{ attachment: sfbuff }], components:rows });
            if (answer == null) {
                message.reply(`Times up!.\n`
                    + `The best discards were: ${game2.bestDiscards}\n`
                    + `Their EVs were: ${game2.evs}`);
            } else {
                let ranking = game2.bestDiscards.indexOf(answer.component.label);
                console.log(answer.component.label);
                console.log(ranking);
                let responseIntro = `You said ${answer.component.label}. `;
                if (ranking > -1) {
                    if (ranking === 0) {
                        responseIntro = responseIntro + `That was the best discard! You earned 5 akocoins!`;
                    } else if (ranking === 4) {
                        responseIntro = responseIntro + `That was the number 5 discard! You earned 1 akocoin!`;
                    } else {
                        responseIntro = responseIntro + `That was the number ${ranking + 1} discard! You earned ${5 - ranking} akocoins!`;
                    }
                }
                message.reply(`${responseIntro}\n`
                    + `The best discards were: ${game2.bestDiscards}\n`
                    + `Their EVs were: ${game2.evs}`);
            }            
        }
    }
});

process.on('SIGINT', function() {
    mongoose.connection.close(function () {
        console.log('Mongoose disconnected on app termination');
        process.exit(0);
    });
});

client.login(config.token);
