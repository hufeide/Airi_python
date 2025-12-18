
from tools.tools import search,browser,code_exec
def tool_agent(state):
    text=state.get("user_input","")
    if "搜索" in text:
        state["tool_result"]=search(text)
    elif "打开" in text:
        state["tool_result"]=browser(text)
    elif "代码" in text:
        state["tool_result"]=code_exec("a=1+1")
    return state
