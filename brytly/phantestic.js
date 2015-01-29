#!/usr/bin/env phantomjs

var page = require('webpage').create();
var system = require('system');
var args = system.args;

page.onConsoleMessage = function (msg, lineNum, sourceId) {
    // Logging is accomplished with 'print' statements, so elide the trailing
    // '\n'.
    console.log(msg.replace(/\n$/, ""));
};

page.onAlert = function(msg) {
    console.log('ALERT: ' + msg);
};

page.onError = function(msg, trace) {
    var msgStack = ['ERROR: ' + msg];
    console.error("PAGE ERROR");
    if (trace && trace.length) {
        msgStack.push('TRACE:');
        trace.forEach(function(t) {
            msgStack.push(' -> ' + t.file + ': ' + t.line +
                          (t['function'] ? ' (in function "' + t['function'] +
                           '")' : ''));
        });
    }
    console.error(msgStack.join('\n'));
    phantom.exit(1);
};

page.onCallback = function (message) {
    // console.log("Phantom Callback." + message.command);
    switch (message.command) {
    case "exit":
        phantom.exit(message.status);
        break;
    case "test-started":
        console.log(message.caseID + ' ... (Start)');
        break;
    case "test-ended":
        var statusMessage;
        if (message.failed) {
            statusMessage = '[FAILED]\n' + message.explanation;
        } else {
            statusMessage = '[OK]';
        }
        console.log(message.caseID + ' ... ' + statusMessage);
        break;
    }
};

if (args.length !== 2) {
    console.log("usage: " + args[0] + " <url>");
    phantom.exit(2);
}

page.open(args[1], function (status) {
    if (status !== 'success') {
        console.log('Unable to access network');
        phantom.exit(1);
    } else {
        console.log("Page loaded, waiting for tests to start...");
    }
});


