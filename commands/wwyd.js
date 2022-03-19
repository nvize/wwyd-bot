const { MessageActionRow, MessageButton } = require('discord.js');
const fs = require('fs');
const spawn = require("child_process").spawn;

const akochanProblems = fs.readdirSync('./akochans');

module.exports = {

    cmdKeyword: ["!wwyd"],

    execute: async function (message) {

        // read in wwyd json file
        let user = message.author;
        //let gameFilepath = `./akochans/${akochanProblems[Math.floor(Math.random() * akochanProblems.length)]}`;
        let gameFilepath = './randWWYD.json' // testing line
        let rawGameFilepathData = fs.readFileSync(gameFilepath);
        let game = JSON.parse(rawGameFilepathData);

        // create python subprocess for generating board picture
        let pythonProcess = spawn('py', ["./scripts/createGameStatePicture.py", gameFilepath, "filepath"])
        let gameImageBase64 = '';
        pythonProcess.stdout.on('data', async (data) => {
            gameImageBase64 += data;
        });

        // create discord message after picture is generated
        pythonProcess.on('close', async function (code) {

            let sfbuff = new Buffer.from(gameImageBase64, 'base64'); // board image
            let rows = []; // buttons for answering wwyd
            for (let x in game.potentialDiscards) {
                if (x % 5 == 0)
                    rows.push(new MessageActionRow())
                rows[Math.floor(x / 5)].addComponents(
                    new MessageButton()
                        .setCustomId(x)
                        .setLabel(game.potentialDiscards[x])
                        .setStyle('PRIMARY')
                );
            }

            let problemReply = await message.reply({ content: `Puzzle name: ${game.name}. You are ${game.seat}.` +
                                                     `Dora indicator: ${game.doraInd}. WWYD? You have 30 seconds to answer!`, 
                                                     files: [{ attachment: sfbuff }], components: rows });
            const filter = i => {
                i.deferUpdate();
                return i.user === user;
            };
            let answer = await message.channel.awaitMessageComponent({ filter, componentType: 'BUTTON', max: 1, time: 30_000 })
                .catch(err => console.log(`No interactions were collected.`));
            rows.forEach(row => row.components.forEach(button => button.setDisabled(true))) // disable buttons after answer / time expires
            problemReply.edit({ content: `Puzzle name: ${game.name}. You are ${game.seat}.` + 
                                `Dora indicator: ${game.doraInd}. WWYD? You have 30 seconds to answer!`, 
                                files: [{ attachment: sfbuff }], components: rows });

            // check answer                    
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
            console.log('done!');
        });
    }

}