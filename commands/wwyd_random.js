const { MessageActionRow, MessageButton } = require('discord.js');
const fs = require('fs');
const spawn = require("child_process").spawn;

const gameLogs = fs.readdirSync('./games');

module.exports = {

    cmdKeyword: ["!wwyd_random"],

    execute: async function (message) {
        wwydRandom(message)
    }

}

// wwyd_random.js //

async function wwydRandom(message) {

    // read in mahjong soul log json file
    let user = message.author;
    //let filePath = `./games/${gameLogs[Math.floor(Math.random() * gameLogs.length)]}`;
    let filePath = `./games/3_3_2022_Gold_Room_South.json` // testing ling
    let rawFileData = fs.readFileSync(filePath);
    let fileData = JSON.parse(rawFileData)

    // choose random round and turn for generating random wwyd
    let numOfRounds = Object.keys(fileData.kyokus).length - 1;
    let round = Math.floor(Math.random() * numOfRounds);
    let numOfTurns = fileData.kyokus[round].entries[fileData.kyokus[round].entries.length - 1].junme;
    let turn = 6 + Math.floor(Math.random() * (numOfTurns - 6));
    console.log(String(round)) // for testing
    console.log(String(turn)) // for testing

    // create python subprocess for generating wwyd problem json file + board state image
    let pythonProcess = spawn('py', ["./scripts/generateTempWWYDProblem.py", filePath, round, turn])
    let gameImageBase64 = '';
    pythonProcess.stdout.on('data', (data) => {
        gameImageBase64 += data;
    });

    // create discord message after picture is generated
    pythonProcess.on('close', async function (code) {

        let gamefile = fs.readFileSync("./randWWYD.json"); // wwyd problem json file
        let game2 = JSON.parse(gamefile)
        let sfbuff = new Buffer.from(gameImageBase64, 'base64'); // board image
        let rows = [];; // buttons for answering wwyd
        for (let x in game2.potentialDiscards) {
            if (x % 5 == 0)
                rows.push(new MessageActionRow())
            rows[Math.floor(x / 5)].addComponents(
                new MessageButton()
                    .setCustomId(x)
                    .setLabel(game2.potentialDiscards[x])
                    .setStyle('PRIMARY')
            );
        }

        let problemReply = await message.reply({
            content: `${filePath}. Round: ${round}. Turn: ${turn}.` +
                `Puzzle name: ${game2.name}. You are ${game2.seat}. Dora indicator: ${game2.doraInd}.` +
                `WWYD? You have 30 seconds to answer!`, files: [{ attachment: sfbuff }], components: rows
        });
        const filter = i => {
            i.deferUpdate();
            return i.user === user;
        };
        let answer = await message.channel.awaitMessageComponent({ filter, componentType: 'BUTTON', max: 1, time: 30_000 })
            .catch(err => console.log(`No interactions were collected.`));
        rows.forEach(row => row.components.forEach(button => button.setDisabled(true))) // disable buttons after answer / time expires
        problemReply.edit({
            content: `${filePath}. Round: ${round}. Turn: ${turn}. Puzzle name: ${game2.name}.` +
                `You are ${game2.seat}. Dora indicator: ${game2.doraInd}. WWYD? You have 30 seconds to answer!`,
            files: [{ attachment: sfbuff }], components: rows
        });

        // check answer
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
    });

}