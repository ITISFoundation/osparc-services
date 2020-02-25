/* eslint-disable no-console */
/* eslint-disable no-undef */

const request = require('request');

const BOOTS_WITH_DEBUGGER = "2"
if (process.env.DEBUG === BOOTS_WITH_DEBUGGER) {
  // Healthcheck disabled with service is boot with a debugger
  console.log(0);
}
else {
  const myArgs = process.argv.slice(2);
  let url = myArgs[0];
  if (myArgs.length > 1) {
    url += myArgs[1]
  }
  console.log(url);
  
  request(url, (error, response) => {
    console.log(response && response.statusCode === 200 ? process.exit(0) : process.exit(1));
  });
}
