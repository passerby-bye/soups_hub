import os
import json
import os

import agentscope
from functools import partial
from moderator import Moderator
from player import Player
from utils import AnswerState, map_response_to_answer_state, check_keywords
from agentscope.message import Msg
from agentscope.agents import UserAgent, DialogAgent
import gradio as gr
import modelscope_studio as mgr
import time
import json

def load_config(config_file_path):
    with open(config_file_path) as config_file:
        config = json.load(config_file)
    api_key = os.environ.get('QW_API_KEY')
    if api_key:
        config[0]['api_key'] = api_key
        config[1]['api_key'] = api_key
    else:
        print("环境变量中未找到 API 密钥")
    return config

config_file_path = "model_configs.json"
config = load_config(config_file_path)





default_turtle_soup = {
    "story": "一个男孩儿走进一家餐厅，喝了一碗海龟汤，然后他就自杀了。为什么？",
    "answer": "这个男孩儿跟爸爸一起出海，中途遇到暴风，在弥留之际，爸爸用自己的肉给他熬了一碗汤，骗他的儿子说这是海龟熬成的汤，爸爸牺牲自己保住了孩子的性命。孩子安全上岸之后，去了餐厅点了一碗真正的海龟汤，发现原来不是那个味道，顿时明白了，就自杀了。",
    "key words": " 父亲，肉，牺牲"
}
keywords = ["父亲", "肉", "牺牲"]

story = default_turtle_soup['story']
ans = default_turtle_soup['answer']
c_sys_prompt = (
    "海龟汤是一种情景推理游戏，是一种猜测情景型事件真相的智力游戏。其玩法是由出题者提出一个难以理解的事件，参与猜题者可以提出任何问题以试图缩小范围并找出事件背后真正的原因，但出题者仅能以是或者不是来回答问题。"
    "游戏谜题本身并没有很强的逻辑性，注重能否发现关键线索重现情景。"
    "接下来，我给你一个经典的故事，叫做“海龟汤”"
    "问题：有一个男子在一家能看见海的餐厅，他点了一碗海龟汤，只吃了几口就惊讶的询问店员：“这真的是海龟汤吗？”，店员回答：”是的，这是货真价实的海龟汤”，于是该名男子就跳下悬崖自杀了，请问这是怎么一回事？"
    "解答：男子以前遭遇海难,快饿死之际男子的同伴递了碗肉汤给他，说里面的是海龟肉，男子这才躲过一劫活了下来；直到此时再次吃到海龟汤，男子发现跟当时的口感完全不同，才突然惊觉当时被同伴骗去吃的正是同伴的肉，受不了打击跑去跳崖"
    "接下来，我继续给你一个汤底和汤面。"
    f"汤面:{story}"
    f"汤底：{ans}"
    "用户是不知道汤底的,你将扮演回答用户问题的角色，并根据我的所有提问来分析我的性格特点（请再次注意，你需要根据我的回答是否贴近故事汤底以及我的逻辑是否清晰进行打分，而不是根据汤面打分）。"
    "你需要根据用户的回答流程是否贴近汤底来判断用户的逻辑思维,而不是回答用户的问题"
    "接下来，请你充当心理学家，生成性格分析的内容并给我打分，请注意，请以用户的提问是否贴近线索以及用户的回答跨度是否很大作为性格判断依据。"
)



#对话框故事
conversation = [
    [
        None,
        {
            # The first message of bot closes the typewriter.
            "text": default_turtle_soup["story"],
            "flushing": False
        }
    ],
]

agentscope.init(config)
moderator = Moderator(model_config_name="moderator")
moderator.init_turtle_soup(default_turtle_soup)
triggered_keywords = set()
logs = ''
c_agent = DialogAgent(
    name='test',
    sys_prompt=c_sys_prompt,
    model_config_name="ca",
    use_memory=True
)


def submit(_input, _chatbot):
    global logs
    msg = Msg(name="user", content=_input.text)

    o_msg = moderator(msg)
    json_msg = o_msg['content']
    json_data = json_msg.strip('```json\n').strip('\n```')

    r_msg = json.loads(json_data)['response']
    logs = logs + _input.text + r_msg

    _chatbot.append([_input, None])
    yield gr.update(interactive=False, value=None), _chatbot
    time.sleep(2)

    _chatbot[-1][1] = {"text": r_msg}
    yield {
        chatbot: _chatbot,
    }


def flushed():
    return gr.update(interactive=True)


def character(_chatbot):
    global logs
    msg = Msg(name="user", content=logs)
    r_msg = c_agent(msg)['content']
    _chatbot.append([logs, None])
    yield gr.update(interactive=False, value=None), _chatbot
    time.sleep(2)

    _chatbot[-1][1] = {"text": r_msg}
    yield {
        chatbot: _chatbot,
    }


with gr.Blocks() as demo:
    chatbot = mgr.Chatbot(
        value=conversation,
        height=600,
    )

    input = mgr.MultimodalInput()
    character_button = gr.Button(value="性格评价")

    input.submit(fn=submit, inputs=[input, chatbot], outputs=[input, chatbot])
    chatbot.flushed(fn=flushed, outputs=[input])

    character_button.click(fn=character, inputs=[chatbot], outputs=[input, chatbot])

if __name__ == "__main__":
    demo.queue()
    demo.launch(share=True)
