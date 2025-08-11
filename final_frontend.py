import streamlit as st
from final_backend import (
    chatbot, 
    retrieve_all_threads, 
    get_thread_summary, 
    save_thread_summary, 
    generate_summary,
    get_all_thread_summaries,
    delete_thread
)
from langchain_core.messages import HumanMessage
import uuid

# **************************************** utility functions *************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []
    st.session_state['current_thread_summary'] = None
    # Don't add to threads list yet - wait for first message

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id, limit=None):
    messages = chatbot.get_state(
        config={'configurable': {'thread_id': thread_id}}
    ).values.get('messages', [])

    if limit:
        return messages[:limit]
    return messages

def ensure_thread_has_summary(thread_id):
    """Check if thread has a summary, generate if not"""
    summary = get_thread_summary(thread_id)
    if not summary:
        # Try to get the first message from the conversation
        messages = load_conversation(thread_id, limit=1)
        if messages and isinstance(messages[0], HumanMessage):
            first_msg = messages[0].content
            summary = generate_summary(first_msg)
            save_thread_summary(thread_id, summary, first_msg)
    return summary


# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    # Get all existing threads
    st.session_state['chat_threads'] = retrieve_all_threads()

if 'current_thread_summary' not in st.session_state:
    st.session_state['current_thread_summary'] = None

# Load summaries for all existing threads (one-time operation)
if 'summaries_loaded' not in st.session_state:
    for thread_id in st.session_state['chat_threads']:
        ensure_thread_has_summary(thread_id)
    st.session_state['summaries_loaded'] = True


# **************************************** Sidebar UI *********************************

st.sidebar.title('🤖 LangGraph Chatbot')

if st.sidebar.button('➕ New Chat', use_container_width=True):
    reset_chat()

st.sidebar.divider()
st.sidebar.header('💬 My Conversations')

# Display threads with summaries
thread_summaries = get_all_thread_summaries()

if thread_summaries:
    for thread_id, summary in thread_summaries:
        # Create a container for better styling
        col1, col2 = st.sidebar.columns([5, 1])
        
        with col1:
            # Display summary as button
            button_label = summary if summary else "Untitled Chat"
            if st.button(button_label, key=f"thread_{thread_id}", use_container_width=True):
                st.session_state['thread_id'] = thread_id
                st.session_state['current_thread_summary'] = summary
                messages = load_conversation(thread_id)

                temp_messages = []

                for msg in messages:
                    if isinstance(msg, HumanMessage):
                        role = 'user'
                    else:
                        role = 'assistant'
                    temp_messages.append({'role': role, 'content': msg.content})

                st.session_state['message_history'] = temp_messages
                st.rerun()
        
        with col2:
            # Optional: Add a delete button for each conversation
            if st.button('🗑️', key=f"del_{thread_id}", help="Delete conversation"):
                delete_thread(thread_id)
                if thread_id in st.session_state['chat_threads']:
                    st.session_state['chat_threads'].remove(thread_id)
                if str(st.session_state['thread_id']) == str(thread_id):
                    reset_chat()
                st.rerun()
else:
    st.sidebar.info("No conversations yet. Start a new chat!")


# **************************************** Main UI ************************************

# Display current conversation summary as title
if st.session_state.get('current_thread_summary'):
    st.title(f"Chat: {st.session_state['current_thread_summary']}")
else:
    st.title("New Conversation")

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input('Type your message here...')

if user_input:
    # If this is the first message in a new chat, generate and save summary
    if len(st.session_state['message_history']) == 0:
        # Generate summary for the first message
        summary = generate_summary(user_input)
        save_thread_summary(st.session_state['thread_id'], summary, user_input)
        st.session_state['current_thread_summary'] = summary
        
        # Add thread to the list
        add_thread(st.session_state['thread_id'])

    # Add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # Get AI response
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    
    # Rerun to update sidebar if this was the first message
    if len(st.session_state['message_history']) == 2:  # First exchange completed
        st.rerun()