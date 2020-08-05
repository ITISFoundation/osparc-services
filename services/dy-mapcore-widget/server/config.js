/* global require */
/* global __dirname */
/* global module */

const path = require('path');
const process = require('process');

module.exports = {
  // webserver configs
  HOSTNAME: '0.0.0.0',
  PORT: 4000,
  BASEPATH: process.env.SIMCORE_NODE_BASEPATH || '',
  APP_PATH: path.resolve(__dirname, '../mapintegratedvuer/dist'),
};
