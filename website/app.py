import ssl
import urllib3
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SSL 검증 비활성화
ssl._create_default_https_context = ssl._create_unverified_context

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import sys
import os
from invest_agent.agent import AllAgent, StockAgent, ETFAgent

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

CURR_DATETIME = "2025-02-08 10:00:00"

# Initialize the three AI assistants
assistants = {
    'all': AllAgent(model="gpt-4.1"),
    'stock': StockAgent(model="gpt-4.1"),
    'etf': ETFAgent(model="gpt-4.1")
}

# Initialize all assistants
for agent in assistants.values():
    agent.reset()
    agent.set_time(CURR_DATETIME)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/initial_guide')
def get_initial_guide():
    """Get the initial guide based on current time"""
    agent_type = request.args.get('agent_type', 'stock')
    try:
        assistant = assistants.get(agent_type, assistants['stock'])
        guide = assistant.get_initial_guide()
        return jsonify({
            'success': True,
            'guide': guide,
            'current_time': CURR_DATETIME,
            'agent_type': agent_type
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@socketio.on('send_message')
def handle_message(data):
    message = data['message']
    agent_type = data.get('agent_type', 'stock')
    assistant = assistants.get(agent_type, assistants['stock'])
    
    response = assistant.generate(message, CURR_DATETIME)
    
    # Handle cases where content might be None (when only tool calls are made)
    if response["content"]:
        content = response["content"]
    elif response["tool_result"]:
        content = f"주문이 실행되었습니다: {response['tool_result']['function']}"
    else:
        content = "응답을 생성했습니다."
    
    # Send the response back to the client
    emit('receive_message', {
        'content': content,
        'tool_calls': response["tool_result_str"],
        'agent_type': agent_type
    })

@socketio.on('set_time')
def handle_set_time(data):
    global CURR_DATETIME
    datetime_str = data['datetime']
    agent_type = data.get('agent_type', 'stock')
    
    # Convert from ISO format (YYYY-MM-DDTHH:MM) to our format (YYYY-MM-DD HH:MM:SS)
    CURR_DATETIME = datetime_str.replace('T', ' ') + ":00"
    
    # Update time for all assistants
    for agent in assistants.values():
        agent.set_time(CURR_DATETIME)
    
    # Get updated initial guide after time change
    try:
        emit('receive_message', {
            'content': f'거래 시간이 {CURR_DATETIME}로 설정되었습니다.',
            'tool_calls': None,
            'agent_type': agent_type
        })
    except Exception as e:
        emit('receive_message', {
            'content': f'거래 시간이 {CURR_DATETIME}로 설정되었습니다.',
            'tool_calls': None,
            'agent_type': agent_type
        })

@socketio.on('reset')
def handle_reset(data):
    agent_type = data.get('agent_type', 'stock')
    assistant = assistants.get(agent_type, assistants['stock'])
    
    assistant.reset()
    assistant.set_time(CURR_DATETIME)
    
    # Get initial guide after reset
    guide = assistant.get_initial_guide()
    
    # Combine reset message and guide into one message
    emit('receive_message', {
        'content': guide,
        'tool_calls': None,
        'agent_type': agent_type
    })
    
if __name__ == '__main__':
    socketio.run(app, debug=True, port=5023) 