from flask import Flask, request, jsonify
from app import (
    top_level_llm,
    wikipedia_agent,
    lazy_gmail_toolkit,
    google_calendar_toolkit,
    create_gmail_draft_wrapper,
)
import json

app = Flask(__name__)

@app.route('/api/ai/process', methods=['POST'])
def process_query():
    try:
        data = request.get_json()
        query = data.get('query')
        if not query:
            return jsonify({'error': 'No query provided'}), 400
            
        response = top_level_llm.invoke(query)
        return jsonify({'result': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/wikipedia', methods=['POST'])
def search_wikipedia():
    try:
        data = request.get_json()
        query = data.get('query')
        if not query:
            return jsonify({'error': 'No query provided'}), 400
            
        response = wikipedia_agent.run(query)
        return jsonify({'result': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/gmail/draft', methods=['POST'])
def create_gmail_draft():
    try:
        data = request.get_json()
        message_details = {
            'message': data.get('message'),
            'to': data.get('to'),
            'subject': data.get('subject')
        }
        
        response = create_gmail_draft_wrapper(json.dumps(message_details))
        return jsonify({'result': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/calendar/event', methods=['POST'])
def create_calendar_event():
    try:
        data = request.get_json()
        event_details = {
            'title': data.get('title'),
            'datetime': data.get('datetime')
        }
        
        response = google_calendar_toolkit.create_event(json.dumps(event_details))
        return jsonify({'result': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
