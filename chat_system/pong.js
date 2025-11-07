const WebSocket = require('ws');

const url = process.argv[2];
if (!url) {
  console.error('Usage: node chat_pong_client.js ws://:port/path?token=YOURTOKEN');
  process.exit(1);
}

const ws = new WebSocket(url);

ws.on('open', () => {
  console.log('Connected!');
});

ws.on('message', (data) => {
  const text = (typeof data === 'string') ? data : data.toString();
  console.log('Received:', text);

  let msg;
  try {
    msg = JSON.parse(text);
  } catch {
    console.log('Non-JSON. Ignored.');
    return;
  }

  if (msg.type === 'ping') {
    ws.send(JSON.stringify({ type: 'pong' }));
    console.log('Sent pong!');
  }
});

ws.on('close', () => {
  console.log('Disconnected.');
  process.exit(0);
});

ws.on('error', (err) => {
  console.error('WebSocket error:', err);
});