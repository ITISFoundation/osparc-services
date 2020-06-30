/* global require */
/* global console */
/* global module */
/* eslint no-console: "off" */

const express = require('express');
const path = require('path');
const events = require('events');
const config = require('./config');

const eventEmitter = new events.EventEmitter()

const appRouter = express.Router();
appRouter.use(express.json())

// handle every other route with index.html, which will contain
// a script tag to your application's JavaScript file(s).
appRouter.get('/', (req, res) => {
  console.log('Routing / to ' + path.resolve(config.APP_PATH, 'index.html'));
  res.sendFile(path.resolve(config.APP_PATH, 'index.html'));
});

module.exports = appRouter;

module.exports.eventEmitter = eventEmitter;
