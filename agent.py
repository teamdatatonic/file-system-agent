# ---- agents/file_system_agent.py ----

import sys
import uuid
import json
from typing import Annotated, Dict, List, Any
from typing_extensions import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import tool

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

# Import tools
from tool import filesystem_tool

# Import config
from config import LLM_MODEL_NAME, LLM_MODEL_TEMPERATURE
from config import ANTHROPIC_API_KEY

##########################################
# 1) Prepare State, Tools and LLM
##########################################


class FileSystemState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

all_tools = [filesystem_tool]

llm = ChatAnthropic(
    model=LLM_MODEL_NAME, 
    temperature=LLM_MODEL_TEMPERATURE, 
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

        ---------------------------------------------------------------
        **What "organizing a messy directory" means**:
        - You might list or walk the directory to see current files and subfolders.
        - Then create needed subdirectories (e.g., 'PDFs', 'Images', etc.).
        - Then move/rename files into place (like converting doc1.PDF => doc1.pdf).
        - Possibly remove old backups or rename them to something consistent.
        - Summarize the final structure for the user.

        **How to go about it**:
        1) Plan your re-organization steps with the user (which subfolders to create, naming conventions, etc.).
        2) Use the appropriate tool actions: 
        - "list" or "walk" to understand structure,
        - "mkdir" to create new folders,
        - "move"/"rename" for rearranging or standardizing names,
        - "remove_file" or "rmdir" for discarding old items,
        - confirm potential data loss or big changes with the user.
        3) Provide short summaries of tool results.

        ---------------------------------------------------------------
        **Examples of multi-step usage**:
        - "list" /Users/me/messy => see items
        - "mkdir" /Users/me/messy/PDFs => create subfolder
        - "search" for *.pdf => gather PDF paths
        - "move" each PDF => /Users/me/messy/PDFs
        - "rename" doc1.PDF => doc1.pdf
        - "remove_file" old_backup.bak => remove clutter
        - "walk" final folder => show final structure

        ---------------------------------------------------------------
        **Agent Best Practices**:
        - Only call filesystem_tool if you need to do an actual operation (avoid loops).
        - Summarize after each action, e.g. "Moved X items to PDFs folder."
        - If an error occurs, gracefully inform the user.
        - Confirm any major destructive steps like removing files or emptying directories.

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

if __name__ == "__main__":
    print("Welcome to the FileSystemAgent! Type 'exit' or 'quit' to stop.\n")
    
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    while True:
        user_text = input("\n[User] ").strip()
        
        if user_text.lower() in ["exit", "quit"]:
            print("Goodbye!")
            sys.exit(0)
            
        if not user_text:
            continue

        # Stream or run the graph with the new user message
        events = agent_graph.stream({"messages": [("user", user_text)]}, config, stream_mode="values")

        for evt in events:
            if "messages" in evt:
                message = evt["messages"][-1]
                
                # Skip user messages
                if hasattr(message, "type") and message.type == "user":
                    continue
                    
                # Handle AIMessage
                if isinstance(message, AIMessage):
                    # Skip if content is a list (tool use message)
                    if isinstance(message.content, list):
                        continue
                    print(f"[Assistant] {message.content}")
                
                # Handle ToolMessage
                elif isinstance(message, ToolMessage):
                    try:
                        result = json.loads(message.content)
                        if isinstance(result, dict) and "result" in result:
                            print(f"[Tool] {result['result']}")
                    except:
                        print(f"[Tool] {message.content}")
                
                print("-"*60)