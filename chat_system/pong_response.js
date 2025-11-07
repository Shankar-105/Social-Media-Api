// Simple pong responder for FastAPI WS ping/pong
// Listens for incoming 'ping' from the server and auto-replies with a 'pong'

const test = require('node:test');
const WebSocket = require('ws');

// This runs when message arrives
function onMessage(ws,data) {
    console.log('Received:', data);  // Log what server sends
    try {
        const text = data.toString();
        const msg = JSON.parse(text);  // Assume JSON
        // check if its a ping or not
        if (msg.type === 'ping') {
            // if its a ping then send a pong reply from the client
            const pongReply = JSON.stringify({ type: 'pong' });
            ws.send(pongReply);  // Send back over WS
            console.log('Sent pong!');
        }
    } catch (e) {
        console.log('Non-JSON or ignore:', data);
    }
}
// wscat calls this setup function when it recives msg from the server
module.exports.setup = function(ws) {
    // bind the handler so ws is available as first param
    ws.on('message', (data) => onMessage(ws,data));
    console.log('Script loaded: Ready for pings!');
};
