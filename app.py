from flask import Flask, render_template, jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from src.prompt import *
import os


app = Flask(__name__)


load_dotenv()

PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


embeddings = download_hugging_face_embeddings()

index_name = "medical-chatbot" 
# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})

# Initialize conversation memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

chatModel = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(chatModel, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)



@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/chat", methods=["GET", "POST"])
def chat():
    # Accept msg from either query string (GET) or form data (POST)
    msg = request.args.get("msg") or request.form.get("msg")
    
    if not msg:
        return jsonify({"error": "Missing 'msg' parameter"}), 400
    
    print(f"User input: {msg}")

    # Add user message to memory
    memory.chat_memory.add_user_message(msg)

    # Invoke chain with chat history
    response = rag_chain.invoke({"input": msg, "chat_history": memory.buffer})
    answer = response["answer"]
    print(f"Response: {answer}")

    # Add AI response to memory
    memory.chat_memory.add_ai_message(answer)
    return str(answer)


@app.route("/history", methods=["GET"])
def get_history():
    """Return chat history for frontend display"""
    history = [
        {
            "type": msg.type,
            "content": msg.content
        }
        for msg in memory.chat_memory.messages
    ]
    return jsonify({"history": history})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 8080, debug= True)