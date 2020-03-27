/* global require */
/* global console */
/* global module */
/* eslint no-console: "off" */

let express = require('express');
const path = require('path');
let appRouter = express.Router();
const events = require('events');
const config = require('./config');
const fs = require('fs');
const spawn = require("child_process").spawn;

let eventEmitter = new events.EventEmitter()

appRouter.use(express.json())

// handle every other route with index.html, which will contain
// a script tag to your application's JavaScript file(s).
appRouter.get('/', function (request, response) {
  console.log('Routing / to ' + path.resolve(config.APP_PATH, 'index.html'));
  response.sendFile(path.resolve(config.APP_PATH, 'index.html'));
});

appRouter.get('/retrieve', callInputRetriever);
appRouter.post('/retrieve', callInputRetriever);

module.exports = appRouter;


function callInputRetriever(request, response) {
  console.log('Received a call to retrieve the data from ' + request.ip);

  copyInputToOutput(response);
  pushFiles(response);
}

function getInputDir() {
  const inputsDir = '../inputs/';
  if (!fs.existsSync(inputsDir)) {
    fs.mkdirSync(inputsDir);
  }
  return inputsDir;
}

function getOutputDir() {
  const outputsDir = '../outputs/';
  if (!fs.existsSync(outputsDir)) {
    fs.mkdirSync(outputsDir);
  }
  const port = "output_1/";
  const outputsDirPort = outputsDir + port;
  if (!fs.existsSync(outputsDirPort)) {
    fs.mkdirSync(outputsDirPort);
  }
  return outputsDirPort;
}

function copyInputToOutput(response) {
  const fileName = "TissueProperties.csv";
  const inFile = getInputDir() + fileName;
  const outFile = getOutputDir() + fileName;
  fs.copyFileSync(inFile, outFile, err => {
    if (err) {
      console.log(err);
      response.status("500");
      throw err;
    }
    console.log(inFile, "was copied to", outFile);
  });
}

function pushFiles(response) {
  var pyProcess = spawn("python3", ["/home/scu/server/input-retriever.py"]);

  pyProcess.on("error", (err) => {
    console.log(`ERROR: ${err}`);
    response.sendStatus("500");
  });

  pyProcess.stdout.setEncoding("utf8");
  pyProcess.stdout.on("data", (data) => {
    console.log(`stdout: ${data}`);
  });

  pyProcess.stderr.on("data", (data) => {
    console.log(`stderr: ${data}`);
  });

  pyProcess.on("close", (code) => {
    console.log(`Function completed with code ${code}.`);
    if (code === 0) {
      const resp = {
        "data": {
          "size_bytes": 1
        }
      };
      response.status("200").send(resp);
      console.log("All went fine");
    }
    else {
      response.sendStatus("500");
      console.log(code, ":(");
    }
  });
}

module.exports.eventEmitter = eventEmitter;
