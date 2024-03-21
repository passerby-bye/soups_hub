from typing import Union, Sequence

from agentscope.agents import DialogAgent
from agentscope.message import Msg

sys_prompt = ('我们来玩一个海龟汤的游戏，下面是海龟汤的定义:\n'
              '海龟汤是一种依靠问答来进行的推理游戏，分为汤底和汤面。在标准流程中，出题者会提供一个有些奇怪的问题，叫做汤面，譬如“一个人被发现熟睡在野外的一截爬梯上，人们叫醒他后他伤心的哭了，请问为什么？”。'
              '而答题者则不断向出题者询问只能用“是”或者“否”来回答的问题，根据答案获得线索并调整猜想，以此为基础提出新的问题，最终完整叙述出整个故事，完整的故事叫做汤底。'
              '下面是海龟汤游戏的过程:\n'
              '1.首先你会把汤面的内容说给我听，但是不会直接告诉我汤底。\n'
              '2.我会不断地问你问题，你可以根据汤底来回答"是""否"或者"不相关" \n'
              '你的回答需要以json对象的形式返回，对象中只包含一个key-value pair，key是response,value包含你对用户问题的回答,对应的value只能是"是","否","不相关"三者中的一个，例如{"response": "是"}'
              )

# sys_prompt = (  '海龟汤游戏：「海龟汤」是玩家们对于情境推理游戏的一种别称。 \n'
#   '游戏玩法很简单，有一个出题者（煲汤人）向玩家讲述一个非常模糊的故事片段（汤面），玩家需要通过不断向出题者提问，一步步推理出故事的真相（汤底）。 \n'
#   '下面是一个海龟汤游戏的例子： \n'
#   '汤面：“一个男孩儿走进一家餐厅，喝了一碗海龟汤，然后他就自杀了。为什么？”  \n'
#   '汤底：“这个男孩儿跟爸爸一起出海，中途遇到暴风，在弥留之际，爸爸用自己的肉给他熬了一碗汤，骗他的儿子说这是海龟熬成的汤，爸爸牺牲自己保住了孩子的性命。孩子安全上岸之后，去了餐厅点了一碗真正的海龟汤，发现原来不是那个味道，顿时明白了，就自杀了。”\n'
#   '在这个过程中，玩家会提出问题，出题者只能回答是、否或者关。现在你来担任出题人，我来担任玩家。 \n'
# )

hint_prompt = ('请你根据海龟汤的汤底，为玩家生成一条提示，注意这个提示不能和之前的提示相似，并且这个提示不能包含太多的汤底，只能包含汤底的一个部分'
               '生成提示的格式为以json 对象的格式返回。每一条提示有一个key-value pairs，key为clue，value为本条线索'
               '例如: {"clue": ...}'
               '下面是你已经生成的提示，请避免生成与下面提示相似的提示:'
               '{}')

story_prompt = ('下面我们开始游戏:'
                '汤面: {}\n'
                '汤底: {}\n'
                '关键词：{}\n')


class Moderator(DialogAgent):
    def __init__(self, model_config_name: str, hint_interval: int = 3, win_interval=3):
        super(Moderator, self).__init__(name="DM", sys_prompt=sys_prompt, use_memory=True,
                                        model_config_name=model_config_name)
        self.hint_interval = hint_interval
        self.win_interval = win_interval
        self.error_round = 0
        self.true_round = 0
        self.clues = []
        self.hints = []
        self.turtle_soup = {}

    def init_turtle_soup(self, turtle_soup) -> None:
        self.turtle_soup = turtle_soup
        prompt = self.engine.join(
            self.sys_prompt,
            story_prompt.format(self.turtle_soup["story"], self.turtle_soup["answer"],self.turtle_soup["key words"]),
            )
        self.memory.add(Msg(self.name,prompt[1:]))
        response = self.model(prompt).text
        self.memory.add(Msg(self.name, response))

    def reply(self, x: dict = None) -> dict:
        if self.memory:
            self.memory.add(x)

        prompt = self.engine.join(self.sys_prompt,self.memory and self.memory.get_memory())
        print(f"user_query: {prompt}")
        response = self.model(prompt).text
        msg = Msg(self.name, response)

        self.speak(msg)
        if self.memory:
            self.memory.add(msg)
        return msg

    def hint(self) -> dict:
        if self.memory:
            self.memory.add()
        prompt = self.engine.join(hint_prompt.format(*self.hints))
        response = self.model(prompt).text
        msg = Msg(self.name,response)
        if self.memory:
            self.memory.add(msg)
        return msg

    def judge_user(self):
        pass
