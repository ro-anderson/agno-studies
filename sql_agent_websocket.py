from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
from sql_agent import get_sql_agent
from datetime import datetime

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>SQL Agent Chat</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            #messages {
                height: 400px;
                overflow-y: auto;
                border: 1px solid #ccc;
                padding: 10px;
                margin: 10px 0;
                background: #f9f9f9;
            }
            .message {
                margin: 5px 0;
                padding: 5px;
                border-radius: 5px;
            }
            .user-message {
                background: #e3f2fd;
                margin-left: 20%;
            }
            .agent-message {
                background: #f5f5f5;
                margin-right: 20%;
            }
            .tool-call {
                background: #fff3e0;
                font-family: monospace;
                padding: 5px;
                margin: 5px 0;
            }
            .event-info {
                font-size: 0.8em;
                color: #666;
                margin-top: 2px;
            }
            form {
                display: flex;
                gap: 10px;
            }
            input[type="text"] {
                flex: 1;
                padding: 8px;
            }
            button {
                padding: 8px 16px;
                background: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background: #1976d2;
            }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                background: #f8f9fa;
                padding: 10px;
                border-radius: 4px;
                margin: 5px 0;
            }
        </style>
    </head>
    <body>
        <h1>SQL Agent Chat</h1>
        <div id="messages"></div>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off" placeholder="Ask about the database..."/>
            <button>Send</button>
        </form>
        <script>
            var ws = new WebSocket(`ws://${window.location.host}/ws`);
            var messages = document.getElementById('messages');
            
            ws.onmessage = function(event) {
                var data = JSON.parse(event.data);
                var messageDiv = document.createElement('div');
                
                // Create the main message container
                messageDiv.className = 'message';
                
                // Add content based on event type
                if (data.event === 'ToolCallStarted') {
                    messageDiv.className += ' tool-call';
                    var toolInfo = data.tools[0];
                    messageDiv.innerHTML = `
                        <div>Tool: ${toolInfo.tool_name}</div>
                        <pre>${JSON.stringify(toolInfo.tool_args, null, 2)}</pre>
                        <div class="event-info">Event: ${data.event}</div>
                    `;
                } else {
                    messageDiv.className += ' agent-message';
                    messageDiv.innerHTML = `
                        <div>${data.content || ''}</div>
                        <div class="event-info">Event: ${data.event}</div>
                    `;
                }
                
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            };

            function sendMessage(event) {
                var input = document.getElementById("messageText");
                var message = input.value;
                
                if (message.trim()) {
                    // Add user message to chat
                    var userDiv = document.createElement('div');
                    userDiv.className = 'message user-message';
                    userDiv.textContent = message;
                    messages.appendChild(userDiv);
                    
                    // Send message to server
                    ws.send(message);
                    input.value = '';
                }
                event.preventDefault();
            }
        </script>
    </body>
</html>
"""

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.sql_agent = get_sql_agent()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_response(self, websocket: WebSocket, response):
        # Convert response to dict and handle datetime objects
        response_dict = {}
        
        # Helper function to safely get attribute value
        def safe_get_attr(obj, attr):
            try:
                value = getattr(obj, attr, None)
                # Convert datetime to string if needed
                if hasattr(value, 'isoformat'):
                    return value.isoformat()
                # Handle MessageMetrics
                if hasattr(value, '__dict__'):
                    return {
                        k: v for k, v in value.__dict__.items()
                        if not k.startswith('_') and v is not None
                    }
                return value
            except Exception:
                return None

        # List of attributes to include
        attributes = [
            'content', 'content_type', 'thinking', 'reasoning_content',
            'event', 'messages', 'metrics', 'model', 'run_id',
            'agent_id', 'session_id', 'workflow_id', 'tools',
            'formatted_tool_calls', 'images', 'videos', 'audio',
            'response_audio', 'citations', 'extra_data', 'created_at'
        ]

        # Safely get each attribute
        for attr in attributes:
            value = safe_get_attr(response, attr)
            if value is not None:
                response_dict[attr] = value

        try:
            # Convert any remaining non-serializable objects to strings
            def make_serializable(obj):
                if isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [make_serializable(item) for item in obj]
                elif hasattr(obj, '__dict__'):
                    return str(obj)
                return obj

            response_dict = make_serializable(response_dict)
            await websocket.send_json(response_dict)
        except Exception as e:
            # If JSON serialization fails, send a simplified version
            simplified_dict = {
                'content': str(response.content) if response.content else None,
                'event': response.event,
                'error': f"Error serializing response: {str(e)}"
            }
            await websocket.send_json(simplified_dict)

manager = ConnectionManager()

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            
            # Stream the agent's response
            response_stream = await manager.sql_agent.arun(message, stream=True, stream_intermediate_steps=True)
            
            async for response in response_stream:
                # Send the complete response data
                await manager.send_response(websocket, response)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket) 