/* global require */
/* global console */
/* global module */
/* eslint no-console: "off" */

let express = require('express');
const path = require('path');
let appRouter = express.Router();
const events = require('events');
const config = require('./config');

let eventEmitter = new events.EventEmitter()

appRouter.use(express.json())

// handle every other route with index.html, which will contain
// a script tag to your application's JavaScript file(s).
appRouter.get('/', function (request, response) {
  console.log('Routing / to ' + path.resolve(config.APP_PATH, 'index.html'));
  response.sendFile(path.resolve(config.APP_PATH, 'index.html'));
});

module.exports = appRouter;


module.exports.eventEmitter = eventEmitter;
