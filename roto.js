//////////////
// ROTO API //
//////////////

// var xhr = new XMLHttpRequest();
// xhr.open('POST', 'https://e6bx9sq57g.execute-api.us-east-1.amazonaws.com/dev/music-vfx-scene');
// xhr.onreadystatechange = function(event) {
//     console.log(event.target.response);
// }
// xhr.send();

// // //


// var request = require('request');

// var options = {
//   url: 'https://e6bx9sq57g.execute-api.us-east-1.amazonaws.com/dev/music-vfx-scene',
//   method: "POST",
//   headers: {
//     'Content-type': 'application/json'
//   },
//   body: '{ "imgId": "123456789" }'
// };

// function callback(error, response, body) {
//     console.log("callback function");
//     if (!error) {
//         var info = (JSON.parse(body));
//         console.log(info);
//         console.log("status 200");

//     }
//     else {
//         console.log(JSON.parse(body));
//     }
// }

// request.post(options, callback);

// // //

const https = require('https');

const data = JSON.stringify({
    sceneId: '999888777'
});

const options = {
    // hostname: 'whatever.com',
    hostname: 'e6bx9sq57g.execute-api.us-east-1.amazonaws.com',
    port: 443,
    // path: '/todos',
    path: '/dev/music-vfx-scene',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
    }
};

const req = https.request(options, res => {
    console.log(`statusCode: ${res.statusCode}`);

    res.on('data', d => {
        process.stdout.write(d);
    })
})

req.on('error', error => {
    console.error(error);
})

req.write(data);
req.end();

///////////
// DEBUG //
///////////

// event:
// {
//     "resource": "/music-vfx-scene",
//     "path": "/music-vfx-scene",
//     "httpMethod": "POST",
//     "headers": {
//         "Accept": "*/*",
//         "Accept-Encoding": "gzip, deflate, br",
//         "Cache-Control": "no-cache",
//         "Host": "e6bx9sq57g.execute-api.us-east-1.amazonaws.com",
//         "Postman-Token": "8f5641e6-c6b9-4d8a-aec1-9d71ac17be81",
//         "User-Agent": "PostmanRuntime/7.26.5",
//         "X-Amzn-Trace-Id": "Root=1-5fa57880-43ff4fdb07a63f5736218266",
//         "X-Forwarded-For": "174.109.251.161",
//         "X-Forwarded-Port": "443",
//         "X-Forwarded-Proto": "https"
//     },
//     "multiValueHeaders": {
//         "Accept": [
//             "*/*"
//         ],
//         "Accept-Encoding": [
//             "gzip, deflate, br"
//         ],
//         "Cache-Control": [
//             "no-cache"
//         ],
//         "Host": [
//             "e6bx9sq57g.execute-api.us-east-1.amazonaws.com"
//         ],
//         "Postman-Token": [
//             "8f5641e6-c6b9-4d8a-aec1-9d71ac17be81"
//         ],
//         "User-Agent": [
//             "PostmanRuntime/7.26.5"
//         ],
//         "X-Amzn-Trace-Id": [
//             "Root=1-5fa57880-43ff4fdb07a63f5736218266"
//         ],
//         "X-Forwarded-For": [
//             "174.109.251.161"
//         ],
//         "X-Forwarded-Port": [
//             "443"
//         ],
//         "X-Forwarded-Proto": [
//             "https"
//         ]
//     },
//     "queryStringParameters": null,
//     "multiValueQueryStringParameters": null,
//     "pathParameters": null,
//     "stageVariables": null,
//     "requestContext": {
//         "resourceId": "smbytm",
//         "resourcePath": "/music-vfx-scene",
//         "httpMethod": "POST",
//         "extendedRequestId": "Vl_EGF_qoAMFXEA=",
//         "requestTime": "06/Nov/2020:16:23:28 +0000",
//         "path": "/dev/music-vfx-scene",
//         "accountId": "808715488150",
//         "protocol": "HTTP/1.1",
//         "stage": "dev",
//         "domainPrefix": "e6bx9sq57g",
//         "requestTimeEpoch": 1604679808596,
//         "requestId": "4e1598a9-5547-4afd-b6aa-6db12e3513ec",
//         "identity": {
//             "cognitoIdentityPoolId": null,
//             "accountId": null,
//             "cognitoIdentityId": null,
//             "caller": null,
//             "sourceIp": "174.109.251.161",
//             "principalOrgId": null,
//             "accessKey": null,
//             "cognitoAuthenticationType": null,
//             "cognitoAuthenticationProvider": null,
//             "userArn": null,
//             "userAgent": "PostmanRuntime/7.26.5",
//             "user": null
//         },
//         "domainName": "e6bx9sq57g.execute-api.us-east-1.amazonaws.com",
//         "apiId": "e6bx9sq57g"
//     },
//     "body": null,
//     "isBase64Encoded": false
// }

// context:
// {
//     "callbackWaitsForEmptyEventLoop": true,
//     "functionVersion": "$LATEST",
//     "functionName": "transformInput",
//     "memoryLimitInMB": "512",
//     "logGroupName": "/aws/lambda/transformInput",
//     "logStreamName": "2020/11/06/[$LATEST]8a0fbf04309e46fe8f67441616d481de",
//     "invokedFunctionArn": "arn:aws:lambda:us-east-1:808715488150:function:transformInput",
//     "awsRequestId": "c9437043-1d15-4eed-b655-d7e5b3744cc6"
// }
