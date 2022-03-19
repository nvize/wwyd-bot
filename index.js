const { Client, Intents } = require('discord.js');
const Discord = require('discord.js');
const { MessageActionRow, MessageButton } = require('discord.js');
const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });
const config = require('./config.json');
const fs = require('fs');
const mongo = require('./mongo.js')
const mongoose = require('mongoose')
const msgCmds = fs.readdirSync('./commands').filter(file => file.endsWith('.js'));

var cmdDict = {};
var btnIDDict = {};

for (const file of msgCmds) {
    let command = require(`./commands/${file}`);
    if (command.cmdKeyword) {
        for (const keyword of command.cmdKeyword) {
            cmdDict[keyword] = command;
        }
    }
    if (command.btnID) {
        for (const id of command.btnID) {
            btnIDDict[id] = command;
        }
    }
}

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
    if (message.content.toLowerCase() in cmdDict) {
        cmdDict[message.content.toLowerCase()].execute(message);
    }
});

client.on('interactionCreate', async interaction => {
    if (interaction.isButton() && interaction.customId in btnIDDict) {
        btnIDDict[interaction.customId].buttonPressed(interaction);
    }
});

process.on('SIGINT', function () {
    mongoose.connection.close(function () {
        console.log('Mongoose disconnected on app termination');
        process.exit(0);
    });
});

client.login(config.token);
