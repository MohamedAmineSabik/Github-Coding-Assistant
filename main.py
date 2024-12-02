import os 
import requests
from dotenv import load_dotenv 
from langchain_core.documents import Document 
from langchain_experimental.chat_models import Llama2Chat
from langchain_astradb import AstraDBVectorStore
from llama_index.core import Settings
from langchain.agents import AgentExecutor,create_tool_calling_agent
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain import hub 
from github import fetch_github_issues
from note import note_tool 
from openai import OpenAI 
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate


load_dotenv 

def connect_to_vstore() : 
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    ASTRA_DB_API_ENDPOINT = "https://f797bcb2-c37b-4e3e-bc4a-911e364b5b01-us-east-2.apps.astra.datastax.com"
    ASTRA_DB_APPLICATION_TOKEN = "AstraCS:PPCvvAAEjbgzUQYyYXfCFwDW:7462eb2e1ec92ce27fb4652468d6cdd0a8087e5c4c762591cff633daf70610b2"
    desired_namespace = os.getenv("ASTRA_DB_KEYSPACE")

    if desired_namespace:
        ASTRA_DB_KEYSPACE = desired_namespace
    else:
        ASTRA_DB_KEYSPACE = None
    vstore = AstraDBVectorStore(
        embedding = embeddings,
        collection_name = "github",
        api_endpoint = ASTRA_DB_API_ENDPOINT,
        token = ASTRA_DB_APPLICATION_TOKEN,
    )   
    return vstore

vstore=connect_to_vstore()
add_to_vectorestore=input("Do you want to update the issues?(y/N)").lower() in ["Yes","y"]
if add_to_vectorestore : 
    owner="techwithtim"
    repo="Flask-Web-App-Tutorial"
    issues=fetch_github_issues(owner,repo)

    try : 
        vstore.delete_collection()
    except : 
        pass 
    vstore=connect_to_vstore()
    vstore.add_documents(issues)


    results=vstore.similarity_search("flash messages" , K=3) 
    for res in results : 
        print(f"*{res.page_content} {res.metadata}")

#Writing the agent 

retriever = vstore.as_retriever(search_kwargs={"k":3})
retriever_tool = create_retriever_tool(
    retriever,
    "github_search",
    "Search for information about github issues. For any questions about github issues , you must use this tool!"
)
template_text="""
You are Llama 2, an advanced and knowledgeable AI assistant. Your purpose is to help users with their queries by providing accurate, concise, and contextually relevant responses to the following question :{question}. Please follow these guidelines:

- **Be precise and clear:** Avoid unnecessary jargon.
- **Stay helpful:** If you're unsure of an answer, provide suggestions for finding the solution.
- **Adapt to the context:** Tailor your responses based on the user's specific request or focus area.
- **Follow ethical guidelines:** Avoid engaging in harmful, biased, or inappropriate behavior.

The user may provide incomplete information. Use reasoning to interpret the query but always ask clarifying questions if needed.

### Example Behavior:

1. **For code generation:**
   Ensure the code is well-documented and functional.
   Use appropriate variable names and comments.

2. **For explanations:**
   Maintain simplicity while ensuring technical correctness.

3. **Formatting:**
   Use markdown for code and structured content when needed for better readability.
"""
prompt=hub.pull("hwchase17/openai-functions-agent")
llm=ChatOpenAI()
tools=[retriever_tool,note_tool]
agent=create_tool_calling_agent(llm,tools,prompt)
agent_executor=AgentExecutor(agent=agent , tools=tools , verbose=True)

while(question:=input("Ask a question about github issues (q to quit) :")) != "q" :
    result=agent_executor.invoke({"input":question})
    print(result["output"])
    