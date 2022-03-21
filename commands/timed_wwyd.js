const { MessageActionRow, MessageButton } = require('discord.js');
const fs = require('fs');
const spawn = require("child_process").spawn;
const cron = require("cron")
const config = require('./../config.json');

const akochanProblems = fs.readdirSync('./akochans');
const gameLogs = fs.readdirSync('./games');

module.exports = {

    cmdKeyword: ["!timedstart", "!timedstop"],
    btnID: ["checkAnswer", "timer0", "timer1", "timer2", "timer3", "timer4", "timer5", "timer6", "timer7", "timer8",
        "timer9", "timer10", "timer11", "timer12", "timer13", "timer14", "timer15", "timer16", "timer17"], // assuming max 18 unique discards...

    execute: async function (message) {
        if (message.content.toLowerCase() == this.cmdKeyword[0]) {
            timerMessageStart(message)
        } else if (message.content.toLowerCase() == this.cmdKeyword[1]) {
            timerMessageStop(message)
        }
    },

    buttonPressed: async function (interaction) {
        if (interaction.customId == this.btnID[0]) {
            checkAnswer(interaction)
        } else {
            logAnswer(interaction)
        }
    }

}

// timed_wwyd.js //

var msgChannel
var timerMessage
var timerMessageCurrent = -1
var timerMessageActive = false
var timerMessageData
var timerMessageMap = new Map();
var timerMessageTime = `00 * * * * *`
var timerMessageFilePath = `./games/${gameLogs[Math.floor(Math.random() * gameLogs.length)]}`;

async function timerMessageStart(message) {
    if (!timerMessageActive) {
        msgChannel = message.channel;
        timerMessage.start()
        timerMessageActive = true
        console.log("timed messages started")
    }
}

async function timerMessageStop(message) {
    if (timerMessageActive) {
        timerMessage.stop()
        if (timerMessageCurrent != -1) {
            let problemMessage = await msgChannel.messages.fetch(timerMessageCurrent)
            let problemMessageContent = problemMessage.content
            let problemMessageButtons = problemMessage.components
            await problemMessageButtons.forEach(row => row.components.forEach(button => button.setDisabled(true)))
            problemMessage.edit({ content: problemMessageContent, components: problemMessageButtons })
        }
        timerMessageActive = false
        console.log("timed messages stopped")
    }
}

async function checkAnswer(interaction) {
    if (timerMessageCurrent == -1) {
        await interaction.reply({ content: `this message has expired!`, ephemeral: true });
        return;
    }
    let userAnsIndex = parseInt(timerMessageMap[interaction.user.id].charAt(timerMessageMap[interaction.user.id].length - 1))
    let ranking = timerMessageData.bestDiscards.indexOf(timerMessageData.potentialDiscards[userAnsIndex]);
    let responseIntro = ``;
    if (ranking > -1) {
        if (ranking === 0) {
            responseIntro = responseIntro + `That was the best discard! You earned 5 akocoins!`;
        } else if (ranking === 4) {
            responseIntro = responseIntro + `That was the number 5 discard! You earned 1 akocoin!`;
        } else {
            responseIntro = responseIntro + `That was the number ${ranking + 1} discard! You earned ${5 - ranking} akocoins!`;
        }
    }
    await interaction.reply({
        content: `You voted for ${timerMessageData.potentialDiscards[userAnsIndex]}.` +
            `${responseIntro}`, ephemeral: true
    });
}

async function logAnswer(interaction) {
    if (timerMessageCurrent == -1) {
        await interaction.reply({ content: `this message has expired!`, ephemeral: true });
        return;
    }
    let userAnsIndex = timerMessageMap[interaction.user.id]
    if (userAnsIndex) { userAnsIndex = parseInt(userAnsIndex[userAnsIndex.length - 1]) }
    let newUserAnsIndex = parseInt(interaction.customId[interaction.customId.length - 1])
    if (timerMessageMap.has(interaction.user.id) && timerMessageMap[interaction.user.id] != interaction.customId) {
        await interaction.reply({
            content: `You changed your vote from ${timerMessageData.potentialDiscards[userAnsIndex]}, to `
                + `${timerMessageData.potentialDiscards[newUserAnsIndex]}.`, ephemeral: true
        });
        timerMessageMap[interaction.user.id] = interaction.customId;
    } else {
        await interaction.reply({ content: `You voted for ${timerMessageData.potentialDiscards[newUserAnsIndex]}.`, ephemeral: true });
        timerMessageMap[interaction.user.id] = interaction.customId;
    }
}

timerMessage = new cron.CronJob(timerMessageTime, async () => {

    msgChannel.send("Hello!")

    if (timerMessageCurrent != -1) {
        let problemMessage = await msgChannel.messages.fetch(timerMessageCurrent)
        let problemMessageContent = problemMessage.content
        let problemMessageButtons = problemMessage.components
        await problemMessageButtons.forEach(row => row.components.forEach(button => button.setDisabled(true)))
        problemMessage.edit({ content: problemMessageContent, components: problemMessageButtons })
    }

    timerMessageFilePath = `./games/${gameLogs[Math.floor(Math.random() * gameLogs.length)]}`;
    console.log(timerMessageFilePath)
    let rawFileData = fs.readFileSync(timerMessageFilePath);
    let fileData = JSON.parse(rawFileData)
    let numOfRounds = Object.keys(fileData.kyokus).length - 1;
    let round = Math.floor(Math.random() * numOfRounds);
    let numOfTurns = fileData.kyokus[round].entries[fileData.kyokus[round].entries.length - 1].junme;
    let turn = 6 + Math.floor(Math.random() * (numOfTurns - 6));
    let pythonProcess = spawn('py', ["./scripts/generateTempWWYDProblem.py", timerMessageFilePath, round, turn])
    let gameImageBase64 = '';
    pythonProcess.stdout.on('data', (data) => {
        gameImageBase64 += data;
    });
    pythonProcess.on('close', async function (code) {
        let gamefile = fs.readFileSync("./randWWYD.json");
        let game2 = JSON.parse(gamefile)
        timerMessageData = JSON.parse(gamefile)
        let sfbuff = new Buffer.from(gameImageBase64, 'base64');
        let rows = [];
        for (let x in game2.potentialDiscards) {
            if (x % 5 == 0)
                rows.push(new MessageActionRow())
            rows[Math.floor(x / 5)].addComponents(
                new MessageButton()
                    .setCustomId(`timer${x}`)
                    .setLabel(game2.potentialDiscards[x])
                    .setStyle('PRIMARY')
            );
        }
        let problemReply = await msgChannel.send({ content: `${timerMessageFilePath}. Round: ${round}. Turn: ${turn}. Puzzle name: ${game2.name}. You are ${game2.seat}. Dora indicator: ${game2.doraInd}. WWYD? You have 30 seconds to answer!`, files: [{ attachment: sfbuff }], components: rows });
        timerMessageCurrent = problemReply.id
        console.log("sent timed wwyd")
    });

    setTimeout(async () => {
        if (timerMessageActive) {
            let problemMessage = await msgChannel.messages.fetch(timerMessageCurrent)
            let problemMessageContent = problemMessage.content
            let problemMessageButtons = problemMessage.components
            let problemMessageImage = problemMessage.attachments
            await problemMessageButtons.forEach(row => row.components.forEach(button => button.setDisabled(true)))
            problemMessage.edit({ content: problemMessageContent, attachment: problemMessageImage.values(), components: problemMessageButtons })
            let rows = new MessageActionRow()
            rows.addComponents(
                new MessageButton()
                    .setCustomId("checkAnswer")
                    .setLabel("Check your answer!")
                    .setStyle('PRIMARY')
            );
            let problemEndMsg = await msgChannel.send({
                content: `Times up!.\n`
                    + `The best discards were: ${timerMessageData.bestDiscards}\n`
                    + `Their EVs were: ${timerMessageData.evs}`, components: [rows]
            });
            timerMessageCurrent = problemEndMsg.id
        }
    }, 45 * 1000);

})