
# 🤖 LangGraph Chatbot

## 📘 Overview  
This project is a conversational **LangGraph Chatbot** that combines memory, multi-threaded conversations, and web search. It provides a smooth user experience with an intuitive Streamlit UI and persistent storage of chats.  

The chatbot automatically generates conversation titles, allows users to manage multiple threads, and integrates with real-time search for up-to-date answers.  

---

## 🖼️ Demo Screenshots  

### Sidebar & Conversations  
![Conversations List](a6838239-ec50-4c67-ae32-1cea49583182.png)

### Example Chat: Nepal’s Latest Conditions  
![Chat Example 1](e67b936e-40b8-41a7-9c1f-e33b482e7fee.png)

### Example Chat: Quick Homemade Pasta  
![Chat Example 2](1c7168c8-f8b4-45d7-82c9-7cd43a357fce.png)

---

## ⚙️ Features
- **Multi-threaded conversations** with summaries  
- **Persistent chat history** stored in SQLite  
- **Auto-generated conversation titles** (3–4 word summaries)  
- **Delete chats** directly from the UI  
- **Web search integration** for real-time answers  
- **Streaming responses** for natural conversation flow  
- **Modern UI** powered by Streamlit  

---

## 🛠️ Technologies Used
- **LangChain** – for LLM integration  
- **LangGraph** – for managing conversation flow and state  
- **Google Gemini (`langchain_google_genai`)** – as the language model  
- **Google Serper API (`langchain_community.utilities`)** – for live search functionality  
- **Streamlit** – for frontend and user interaction  
- **SQLite** – for storing conversations and summaries  
- **Python Dotenv** – for managing API keys securely  

---

## 📌 Example Use Cases
- Real-time news and event queries  
- Recipe or “how-to” assistance  
- Knowledge Q&A with persistent context  
- Managing multiple conversations on different topics  
