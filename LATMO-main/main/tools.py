import json
from datetime import datetime
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.utils import build_resource_service, get_gmail_credentials
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import shutil

class WikipediaTool:
    def __init__(self):
        self.wikipedia = WikipediaAPIWrapper()

    def run(self, query):
        return self.wikipedia.run(query)

class DuckDuckGoTool:
    def __init__(self):
        self.search = DuckDuckGoSearchRun()

    def run(self, query):
        return self.search.run(query)

class GmailTool:
    def __init__(self):
        credentials = get_gmail_credentials(
            token_file="token.json",
            scopes=["https://mail.google.com/"],
            client_secrets_file="credentials.json",
        )
        api_resource = build_resource_service(credentials=credentials)
        self.gmail_toolkit = GmailToolkit(api_resource=api_resource)

    def create_draft(self, message, to, subject):
        create_draft_tool = [tool for tool in self.gmail_toolkit.get_tools() if tool.name == "create_gmail_draft"][0]
        return create_draft_tool.run({"message": message, "to": to, "subject": subject})

    def send_message(self, message, to, subject):
        send_message_tool = [tool for tool in self.gmail_toolkit.get_tools() if tool.name == "send_gmail_message"][0]
        return send_message_tool.run({"message": message, "to": to, "subject": subject})

    def search_gmail(self, query, limit=10):
        search_tool = [tool for tool in self.gmail_toolkit.get_tools() if tool.name == "search_gmail"][0]
        return search_tool.run({"query": query, "limit": limit})

    def get_message(self, message_id):
        get_message_tool = [tool for tool in self.gmail_toolkit.get_tools() if tool.name == "get_gmail_message"][0]
        return get_message_tool.run({"message_id": message_id})

    def get_thread(self, thread_id):
        get_thread_tool = [tool for tool in self.gmail_toolkit.get_tools() if tool.name == "get_gmail_thread"][0]
        return get_thread_tool.run({"thread_id": thread_id})

    def run(self, input_str):
        input_dict = json.loads(input_str)
        action = input_dict.get('action')
        if action == 'create_draft':
            return self.create_draft(input_dict.get('message'), input_dict.get('to'), input_dict.get('subject'))
        elif action == 'send_message':
            return self.send_message(input_dict.get('message'), input_dict.get('to'), input_dict.get('subject'))
        elif action == 'search':
            return self.search_gmail(input_dict.get('query'), input_dict.get('limit', 10))
        elif action == 'get_message':
            return self.get_message(input_dict.get('message_id'))
        elif action == 'get_thread':
            return self.get_thread(input_dict.get('thread_id'))
        else:
            return "Invalid action specified for Gmail tool."

class LocalRAGTool:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_directory = os.path.join(os.getcwd(), "local_chroma_db")
        self.vector_store = Chroma(
            "local_memory_store",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        self.text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def add_to_memory(self, input_str):
        input_dict = json.loads(input_str)
        text = input_dict.get('text', '')
        chunks = self.text_splitter.split_text(text)
        self.vector_store.add_texts(chunks)
        self.vector_store.persist()
        return f"Added {len(chunks)} chunks to local memory and persisted changes."

    def query_memory(self, input_str):
        input_dict = json.loads(input_str)
        query = input_dict.get('query', '')
        results = self.vector_store.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in results])
        return context if context.strip() else "No relevant information found in memory."

    def clear_memory(self):
        shutil.rmtree(self.persist_directory, ignore_errors=True)
        self.vector_store = Chroma(
            "local_memory_store",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        return "Chroma DB has been cleared successfully."

    def run(self, input_str):
        input_dict = json.loads(input_str)
        action = input_dict.get('action')
        if action == 'add':
            return self.add_to_memory(json.dumps(input_dict))
        elif action == 'query':
            return self.query_memory(json.dumps(input_dict))
        elif action == 'clear':
            return self.clear_memory()
        else:
            return "Invalid action specified for Local RAG tool."

class GoogleCalendarTool:
    def __init__(self):
        self.credentials = self.get_google_calendar_credentials()
        self.service = build('calendar', 'v3', credentials=self.credentials)

    def get_google_calendar_credentials(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', ['https://www.googleapis.com/auth/calendar'])
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds

    def create_event(self, summary, start_time, end_time, description):
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        }
        created_event = self.service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {created_event.get('htmlLink')}"

    def list_events(self, max_results=10, time_min=None):
        if time_min is None:
            time_min = datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(calendarId='primary', timeMin=time_min,
                                                   maxResults=max_results, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            return "No upcoming events found."
        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_list.append(f"{start} - {event['summary']}")
        return "\n".join(event_list)

    def view_event(self, event_id):
        event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        return f"Event: {event['summary']}\nStart: {start}\nEnd: {end}\nDescription: {event.get('description', 'N/A')}"

    def run(self, input_str):
        input_dict = json.loads(input_str)
        action = input_dict.get('action')
        if action == 'create_event':
            return self.create_event(input_dict.get('summary'), input_dict.get('start_time'),
                                     input_dict.get('end_time'), input_dict.get('description'))
        elif action == 'list_events':
            return self.list_events(input_dict.get('max_results', 10), input_dict.get('time_min'))
        elif action == 'view_event':
            return self.view_event(input_dict.get('event_id'))
        else:
            return "Invalid action specified for Google Calendar tool."

class DatetimeTool:
    def run(self, query):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class CoderTool:
    def run(self, query):
        # This is a placeholder. In a real implementation, you'd need to integrate
        # with a code generation model or service.
        return f"Here's a code snippet for your query: '{query}'\n\n```python\n# Code goes here\n```"