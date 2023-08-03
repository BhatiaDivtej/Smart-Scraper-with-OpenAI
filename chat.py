import openai
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import os
from langchain.embeddings.openai import OpenAIEmbeddings
import openai
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI


# Load environment variables from a .env file
load_dotenv()

website_url = os.environ.get('WEBSITE_URL', 'a website')
# Set the title for the Streamlit app
st.title(f'A50 Real Assets Limited - Large Language Model')
st.title(f'A.I. now understands: {website_url}')

# Set the OpenAI API key from the environment variable
openai.api_key = os.environ.get('OPENAI_API_KEY')
# Create an instance of OpenAIEmbeddings
embeddings = OpenAIEmbeddings()

# Create an instance of Chroma
db = Chroma(persist_directory='db', embedding_function=embeddings)


def get_text():
    # Create a Streamlit input field and return the user's input
    input_text = st.text_input("", key="input")
    return input_text

def get_qa():
    template = """You are a chatbot having a conversation with a human.

    Given the following extracted parts of a long document and a question, create a final answer.

    {context}

    {chat_history}
    Human: {human_input}
    Chatbot:"""

    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input", "context"], 
        template=template
    )
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")
    chain = load_qa_chain(ChatOpenAI(model='gpt-3.5-turbo', temperature=0), chain_type="stuff", memory=memory, prompt=prompt)
    return chain

def query(user_input, chain):
    docs = db.similarity_search(user_input)
    return chain({"input_documents": docs, "human_input": user_input}, return_only_outputs=True)['output_text']

if 'qa' not in st.session_state:
    st.session_state['qa'] = get_qa()

# Initialize the session state for generated responses and past inputs
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

# Get the user's input from the text input field
user_input = get_text()

# If there is user input, search for a response using the search_db function
if user_input:
    output = query(user_input, st.session_state['qa'])
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

# If there are generated responses, display the conversation using Streamlit messages
if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])):
        message(st.session_state['past'][i],
                is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))
