# ---- agents/file_system_agent.py ----

import sys
import uuid
import json
from typing import Annotated, Dict, List, Any
from typing_extensions import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage, HumanMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import tool

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

# Import tools
from tool import filesystem_tool

# Import config
from config import LLM_MODEL_NAME, ANTHROPIC_API_KEY

##########################################
# 1) Prepare State, Tools and LLM
##########################################


class FileSystemState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

all_tools = [filesystem_tool]

llm = ChatAnthropic(
    model=LLM_MODEL_NAME, 
    temperature=0, 
    api_key=ANTHROPIC_API_KEY
)

system_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        
        """You are a FileSystemAgent with these capabilities (via filesystem_tool(action=...)):
        1. list => list items in a directory
        2. search => search for files by pattern under a root
        3. read => read text content of a file
        4. write => write or append text content to a file
        5. grep => find lines containing some text
        6. uuid => generate a new UUID
        7. resolve => recursively find a file/directory name in a root directory
        8. mkdir => create a directory
        9. rmdir => remove an empty directory
        10. remove_file => remove a single file
        11. rename => rename or move a file/directory from 'path' -> 'dst'
        12. move => move a file or directory from 'src' -> 'dst'
        13. copy => copy a file or directory from 'src' -> 'dst'
        14. walk => retrieve a structured tree of an entire directory
        15. path_info => get metadata about a path
        16. pwd => print working directory (get current directory path)


        ===== Answer Formatting Guidelines =====
        1. always be highly highly concrete and concise in your answers.
        2. if you read content of a file, don't print out the content of the file to the user (it'd flood the logs)
        3. before removing or moving a file, always first get a yes/no confirmation from the user.
        
        ===== Capabilities ======
        ## 1. Directory Organization Instructions**:

        If user asks: "please organize the documents/forms folder"

        Step1: create sibling 'organized_[<target_directory_name>]/' directory (sibiling to the target directory):
           
           example1: Target: '/documents/forms/'  →  Create: '/documents/organized_[forms]/'
           example2: Target: './src/old/'        →  Create: './src/organized_[old]/'
           
        Step2: Copy files to sibling directory:
        example:
           FROM: './src/old/Form.pdf'
           TO:   './src/organized_[old]/pdf/Form1234_OLD_CLIENTS.pdf'
           
        Step3: Standardize in organized/:
           - Lowercase with underscores
           - Group by type: pdfs/, docs/, etc.
        example:
           FROM: './src/organized_[old]/pdf/Form1234_OLD_CLIENTS.pdf'
           TO:   './src/organized_[old]/pdf/form_1234_old_clients.pdf'
        
        End of instructions.
        """
    ),
    ("placeholder", "{messages}")
])

llm_with_tools = llm.bind_tools(all_tools)

##########################################
# 3) Define Chat Node
##########################################

def chatbot(state: FileSystemState) -> Dict[str, List[BaseMessage]]:
    """Process user messages, optionally call filesystem_tool, then return new response."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

##########################################
# 4) Build the Graph
##########################################

graph_builder = StateGraph(FileSystemState)

# Add a tool node that can handle tool calls
tool_node = ToolNode(tools=all_tools)
graph_builder.add_node("tools", tool_node)

# Add main chat node
graph_builder.add_node("chatbot", chatbot)

# If the LLM decides to call a tool, go to 'tools'
graph_builder.add_conditional_edges("chatbot", tools_condition)

# After 'tools' is done, come back to 'chatbot'
graph_builder.add_edge("tools", "chatbot")

# Start at 'chatbot'
graph_builder.set_entry_point("chatbot")

# Compile with memory
memory = MemorySaver()
agent_graph = graph_builder.compile(checkpointer=memory)

##########################################
# 5) Example Interactive Loop
##########################################

def print_message(message):
    if isinstance(message, AIMessage):
        if isinstance(message.content, list):
            # For tool calls, just show the tool being called
            for item in message.content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    print(f"Tool Call: {item.get('name')}({item.get('input', {})})")
        else:
            # For regular responses
            print(f"Assistant: {message.content}")
    elif isinstance(message, ToolMessage):
        try:
            # Try to pretty print JSON responses
            result = json.loads(message.content)
            print(f"Tool Result: {result}")
        except:
            print(f"Tool Result: {message.content}")
    # elif isinstance(message, HumanMessage):
        # print(f"\nHuman: {message.content}")
    print("-" * 80)

if __name__ == "__main__":
    print("Welcome to the File System Agent! Type 'exit' or 'quit' to stop.\n")
    
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    while True:
        user_text = input("Human: ").strip()
        
        if user_text.lower() in ["exit", "quit"]:
            print("Goodbye!")
            sys.exit(0)
            
        if not user_text:
            continue

        events = agent_graph.stream({"messages": [("user", user_text)]}, config, stream_mode="values")

        for evt in events:
            if "messages" in evt:
                message = evt["messages"][-1]
                print_message(message)