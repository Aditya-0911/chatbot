from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph,START,END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os
import json

load_dotenv()
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

class chatstate(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state:chatstate)->chatstate:
    messages = state['messages']
    response = model.invoke(messages)
    return {'messages':[response]}


DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot2.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# Create thread summaries table if it doesn't exist
conn.execute('''
    CREATE TABLE IF NOT EXISTS thread_summaries (
        thread_id TEXT PRIMARY KEY,
        summary TEXT NOT NULL,
        first_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(chatstate)

# add nodes
graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

#**************************** Utilities ****************************

def retrieve_all_threads():
    """Retrieve all thread IDs from checkpointer"""
    threads = []
    seen = set()
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config['configurable']['thread_id']
        if thread_id not in seen:
            seen.add(thread_id)
            threads.append(thread_id)
    return threads

def get_thread_summary(thread_id):
    """Get the summary for a specific thread from database"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT summary FROM thread_summaries WHERE thread_id = ?", 
        (str(thread_id),)
    )
    result = cursor.fetchone()
    return result[0] if result else None

def save_thread_summary(thread_id, summary, first_message):
    """Save thread summary to database"""
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR REPLACE INTO thread_summaries 
           (thread_id, summary, first_message) 
           VALUES (?, ?, ?)""",
        (str(thread_id), summary, first_message)
    )
    conn.commit()

def generate_summary(message_text):
    """Generate a 3-4 word summary of the message using the model"""
    prompt = f"""Generate a very brief 3-4 word summary or title for this message. 
    Only return the summary, nothing else.
    Message: {message_text}"""
    
    try:
        response = model.invoke(prompt)
        summary = response.content.strip()
        # Ensure summary is not too long
        words = summary.split()
        if len(words) > 5:
            summary = ' '.join(words[:4]) + '...'
        return summary
    except Exception as e:
        # Fallback to simple truncation if model fails
        words = message_text.split()[:4]
        return ' '.join(words) + '...' if len(words) >= 4 else message_text[:20] + '...'

def get_all_thread_summaries():
    """Get all threads with their summaries"""
    cursor = conn.cursor()
    cursor.execute(
        """SELECT thread_id, summary, created_at 
           FROM thread_summaries 
           ORDER BY created_at DESC"""
    )
    results = cursor.fetchall()
    return [(row[0], row[1]) for row in results]

def delete_thread(thread_id):
    """Delete a thread and its summary"""
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM thread_summaries WHERE thread_id = ?",
        (str(thread_id),)
    )
    conn.commit()

    # Note: You might also want to delete from checkpointer, but that depends on your needs
