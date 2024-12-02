from langchain_core.tools import tool 
@tool
def note_tool(note) : 
    #we will write a docstring like a metadata that describe brievely the tool 
    """
    saves a note to a local file 
    Args : 
        note : the text note to save 

    """
# we will use the decorator tool that can be passed as a langchain tool for our agent 
    with open("notes.txt","a") as f : 
        f.write(note + "\n")
 