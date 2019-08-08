'use strict';

const cfSign = require('aws-cloudfront-sign');
const config = require('./config.json');
const baseUrl = config.videos.distribution.baseUrl;
const keypairId = config.videos.distribution.keyPairId;
const privateKey = config.videos.distribution.privateKey;

const oneHour = 60 * 60 * 1000;

const getExpireTime = (date, offset) => {
  // expireTime value can be milliseconds, Date, or moment
  return date.getTime() + parseInt(offset);
};

const getResponse = (code, body) => {
  return {
    statusCode: code,
    body: JSON.stringify(body)
  }
};

const generate = (event, context, callback) => {
  const file = event.file;

  if (file) {
    const signingParams = {
      keypairId: keypairId,
      privateKeyString: privateKey,
      expireTime: getExpireTime(new Date(), oneHour * 24)
    }
    const url = baseUrl + file;
    const signedUrl = cfSign.getSignedUrl(url, signingParams)
    callback(null, getResponse(200, { 'signedUrl': signedUrl }));
  }
  else {
    console.error('Missing file');
    callback(null, getResponse(400, { 'errorMessage': 'Missing file' }));
  }
};

module.exports = {
  generate: generate
};
