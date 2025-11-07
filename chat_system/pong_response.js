// pong_response.js
// wscat script: listens for JSON {"type":"ping"} and replies {"type":"pong"}

module.exports.setup = function (ws) {
  console.log('pong_response script loaded — ready for pings');

  ws.on('message', (data) => {
    // ensure we have a string
    const text = (typeof data === 'string') ? data : data.toString();
    console.log('Received raw:', text);

    try {
      const msg = JSON.parse(text);
      if (msg && msg.type === 'ping') {
        // reply with a JSON pong
        ws.send(JSON.stringify({ type:'pong' }));
        console.log('Sent pong!');
      } else {
        // Not a ping — you can log or ignore
        console.log('Not a ping (ignored):', msg);
      }
    } catch (err) {
      // Not JSON — ignore or log plain text
      console.log('Non-JSON message (ignored):', text);
    }
  });

  ws.on('close', () => console.log('Client socket closed'));
  ws.on('error', (err) => console.error('Client socket error:', err));
};