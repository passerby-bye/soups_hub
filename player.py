from agentscope.agents import AgentBase
from agentscope.message import Msg



class Player(AgentBase):
    def __init__(self,name="Player"):
        super().__init__(name="Player",use_memory=True)

    def reply(self, x: dict = None) -> dict:
        content = input(f"{self.name}: ")
        msg = Msg(name=self.name, content=content,role="user")
        if self.memory:
            self.memory.add(msg)
        return msg, content
    
