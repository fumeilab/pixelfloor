# PixelFloor

**A drop-in pixel-art visualization for AI agent pipelines.**

PixelFloor renders a cozy office where pixel characters represent your agents. They work, celebrate, chat, and pass data to each other in real-time. Use it standalone as a demo or connect it to a live backend via WebSocket to watch your pipeline come alive.

[screenshot placeholder]

---

## Features

- **Single HTML file** -- zero dependencies, zero build step, just open it
- **9 hand-crafted pixel sprites** -- detective, hacker, scientist, analyst, researcher, manager, trader, cowboy, engineer
- **60fps HTML5 Canvas** with pre-rendered tiled backgrounds and smooth animation
- **Data flow particles** trace bezier curves between agents to visualize your pipeline
- **Agent states** -- idle, working, celebrating, error -- with speech bubbles, sparkle effects, and status dots
- **Interactive** -- click agents for a detail side panel; click office objects (water cooler, pizza, snack machine) for fun
- **Day/night cycle** with animated monitors showing charts, coffee steam particles, and a neon office sign
- **Real-time integration** via WebSocket or direct JavaScript API
- **Python server included** (FastAPI) for log file tailing and REST event endpoints
- **MIT licensed** -- use it however you want

---

## Quick Start

### 1. Just open it

```bash
# That's it. Demo mode auto-runs with 9 sample agents.
open index.html
# or
xdg-open index.html
```

### 2. With the Python server

```bash
pip install -r requirements.txt
python server.py
# Visit http://localhost:8420
```

### 3. With a custom config

Add a `<script>` tag before the closing `</body>`, or load it after `index.html`:

```html
<script>
const floor = new PixelFloor({
  title: 'My Pipeline',
  agents: [
    { id: 'scanner', name: 'Scout', role: 'Data Collector', color: '#B8860B', sprite: 'detective', position: 0 },
    { id: 'processor', name: 'Nova', role: 'Analyzer', color: '#8B5CF6', sprite: 'analyst', position: 1 },
    { id: 'output', name: 'Echo', role: 'Reporter', color: '#06B6D4', sprite: 'engineer', position: 2 },
  ],
  flows: [
    { from: 'scanner', to: 'processor' },
    { from: 'processor', to: 'output' },
  ],
  websocket: 'ws://localhost:8420/ws',  // optional -- omit for JS-only control
});
</script>
```

---

## Configuration

The `PixelFloor` constructor accepts a single config object:

```js
const floor = new PixelFloor({
  title: 'My Pipeline',          // Displayed in the header bar
  agents: [
    {
      id: 'scanner',             // Unique identifier (used in API calls)
      name: 'Scout',             // Display name
      role: 'Data Collector',    // Subtitle shown in tooltips and side panel
      color: '#B8860B',          // Accent color for status dot and particles
      sprite: 'detective',       // One of the 9 built-in sprites
      position: 0,               // Desk position (0-8, left to right)
    },
    // ... more agents
  ],
  flows: [
    { from: 'scanner', to: 'processor' },  // Defines particle paths
  ],
  websocket: 'ws://localhost:8420/ws',      // Optional WebSocket URL
});
```

If `websocket` is omitted, PixelFloor runs in demo mode with simulated activity.

---

## JavaScript API

All methods are available on the `PixelFloor` instance:

### `agentWorking(id, speech?, duration?)`

Set an agent to the working state. They lean into their monitor and a colored status dot appears.

```js
floor.agentWorking('scanner', 'Scanning feeds...', 400);
```

### `agentCelebrating(id, speech?, duration?)`

Trigger a celebration -- the agent jumps and sparkles appear.

```js
floor.agentCelebrating('processor', 'Found a match!', 300);
```

### `agentError(id, speech?, duration?)`

Put an agent into error state with a red status indicator.

```js
floor.agentError('output', 'Connection lost', 480);
```

### `agentIdle(id)`

Return an agent to their default idle state.

```js
floor.agentIdle('scanner');
```

### `sendParticle(fromId, toId)`

Send a glowing data particle along the flow path between two agents. Works even if no flow was pre-defined (an ad-hoc path is created automatically).

```js
floor.sendParticle('scanner', 'processor');
```

### `flash(duration?)`

Flash the entire screen white -- useful for signaling major events. Duration is in frames (default 600).

```js
floor.flash(400);
```

### `pushLog(text, type?)`

Push a line to the log feed at the bottom of the screen. Types: `"info"`, `"success"`, `"error"`, `"highlight"`, `"special"`.

```js
floor.pushLog('Batch complete: 42 items processed', 'success');
```

### `setMetric(value)`

Set the metric counter displayed in the header bar. Pass a number -- positive values show green, negative show red.

```js
floor.setMetric(1547);
```

---

## Available Sprites

| Sprite       | Description                         | Default Color |
|--------------|-------------------------------------|---------------|
| `detective`  | Fedora, trench coat, press badge    | `#B8860B`     |
| `hacker`     | Blue hoodie, headphones             | `#4A90D9`     |
| `scientist`  | Glasses, hair bun, lab coat         | `#E8B830`     |
| `analyst`    | Dark hair, purple hoodie            | `#8B5CF6`     |
| `researcher` | Teal hair, white lab coat, glasses  | `#22D3EE`     |
| `manager`    | Red blazer, glasses, clipboard      | `#DC2626`     |
| `trader`     | Green jacket, bob haircut           | `#16A34A`     |
| `cowboy`     | Cowboy hat, orange vest             | `#EA580C`     |
| `engineer`   | Cyan sweater, spiky blue hair       | `#06B6D4`     |

All sprites are 16x16 pixel art with idle and walk frames, rendered at runtime on the canvas. You can assign any sprite to any agent regardless of its default color -- the `color` field in your config controls the accent color independently.

---

## WebSocket Protocol

Connect to the WebSocket endpoint and send JSON messages to control the visualization in real-time.

### `agent_state`

```json
{
  "type": "agent_state",
  "agent": "scanner",
  "state": "working",
  "speech": "Processing...",
  "duration": 300
}
```

Valid states: `"working"`, `"celebrating"`, `"error"`, `"idle"`.

### `particle`

```json
{
  "type": "particle",
  "from": "scanner",
  "to": "processor"
}
```

### `log`

```json
{
  "type": "log",
  "text": "Event received from upstream",
  "level": "info"
}
```

### `flash`

```json
{
  "type": "flash",
  "duration": 600
}
```

---

## Server

`server.py` is a lightweight FastAPI server that serves `index.html` and relays WebSocket messages between clients. It can also tail a log file and broadcast new lines.

### Usage

```bash
python server.py                              # Serve on port 8420
python server.py --port 3000                  # Custom port
python server.py --log-file myapp.log         # Tail a log file and broadcast lines
```

### REST Endpoints

For systems that prefer HTTP over WebSocket, the server exposes REST endpoints that broadcast to all connected clients:

| Method | Endpoint         | Body                                                        |
|--------|------------------|-------------------------------------------------------------|
| POST   | `/api/event`     | `{ "agent": "id", "state": "working", "speech": "...", "duration": 300 }` |
| POST   | `/api/log`       | `{ "text": "Log message", "level": "info" }`               |
| POST   | `/api/particle`  | `{ "from_agent": "id1", "to_agent": "id2" }`               |
| POST   | `/api/flash`     | Query param: `?duration=600`                                |

```bash
# Example: trigger an agent state change via curl
curl -X POST http://localhost:8420/api/event \
  -H "Content-Type: application/json" \
  -d '{"agent": "scanner", "state": "celebrating", "speech": "Done!", "duration": 300}'
```

---

## Integration Examples

### Python (WebSocket)

```python
import asyncio
import json
import websockets

async def notify_pixelfloor():
    async with websockets.connect("ws://localhost:8420/ws") as ws:
        # Set an agent to working
        await ws.send(json.dumps({
            "type": "agent_state",
            "agent": "analyzer",
            "state": "working",
            "speech": "Processing batch..."
        }))

        # Send a data particle
        await ws.send(json.dumps({
            "type": "particle",
            "from": "scanner",
            "to": "analyzer"
        }))

        # Log a message
        await ws.send(json.dumps({
            "type": "log",
            "text": "Batch 47 started",
            "level": "info"
        }))

asyncio.run(notify_pixelfloor())
```

### Python (REST)

```python
import requests

requests.post("http://localhost:8420/api/event", json={
    "agent": "scanner",
    "state": "celebrating",
    "speech": "Found 3 results!",
    "duration": 400,
})
```

### Node.js

```js
const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:8420/ws');

ws.on('open', () => {
  ws.send(JSON.stringify({
    type: 'agent_state',
    agent: 'processor',
    state: 'working',
    speech: 'Crunching numbers...',
  }));
});
```

---

## License

MIT -- see [LICENSE](LICENSE).

Built with care and too much coffee.
