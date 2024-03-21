# -*- coding: utf-8 -*-

import base64

import gradio as gr
import modelscope_studio as mgr
import re
import time
#enable_web_ui()




# 图片本地路径转换为 base64 格式
def covert_image_to_base64(image_path):

    ext = image_path.split(".")[-1]
    if ext not in ["gif", "jpeg", "png"]:
        ext = "jpeg"

    with open(image_path, "rb") as image_file:
        # Read the file
        encoded_string = base64.b64encode(image_file.read())

        # Convert bytes to string
        base64_data = encoded_string.decode("utf-8")

        # 生成base64编码的地址
        base64_url = f"data:image/{ext};base64,{base64_data}"
        return base64_url



def get_clue():
    global glb_clue_dict

    # uid = check_uuid(uid)
    # clue_item = get_clue_msg(uid)

    flex_container_html_list = """
    <div class="hint">查看已解锁线索卡片</div>
    <div class="mytabs">
        <div class='clue-card clue-card-locked'>
            <div style='flex-grow: 1; width: 100%; background-color: #bbb; border-radius: 10px; margin-bottom: 10px; display: flex; align-items: center; justify-content: center;'>
                <!--  <<h4 style='margin: 5px 0; text-align: center; word-wrap: break-word; font-size: 18px; font-weight: bold; color: #999;'>?</h4>-->
                    <span class='lock-icon'>&#128274;</span>
            </div>
                <h4 style='margin: 5px 0; text-align: center; word-wrap: break-word; font-size: 18px; font-weight: bold; color: #999;'>待发现</h4>
                </div>
    </div>
    </div>
    """
    return gr.HTML(flex_container_html_list)







if __name__ == "__main__":

    with gr.Blocks(css="assets/app.css") as demo:

        game_tabs = gr.Tabs(visible=True)
        #
        with game_tabs:
             main_tab = gr.Tab('主界面', id=0)
             riddle_tab = gr.Tab('人格测试结果', id=1)
             with main_tab:
                 with gr.Row():
                     with gr.Row():
                         with gr.Column():
                             story_text=gr.Text(
                                 label="海龟汤题目",
                                 lines=10,
                                 value="海龟汤内容"),
                             clue_container = gr.HTML()
                         with gr.Column():
                             chatbot = mgr.Chatbot(
                                 elem_classes="app-chatbot",
                                 label="Dialog",
                                 show_label=False,
                                 bubble_full_width=False,
                             )
                             input = mgr.MultimodalInput()

             with gr.Row():
                 return_welcome_button = gr.Button(value="↩️返回首页")


        def game_ui():
             return gr.update(visible=False), gr.update(visible=True)


        def submit(_input, _chatbot):
            _chatbot.append([_input, None])
            yield gr.update(interactive=False, value=None), _chatbot
            time.sleep(2)


            _chatbot[-1][1] = {"text": _input.text + '!'}
            yield {
                chatbot: _chatbot,
            }


        def flushed():
            return gr.update(interactive=True)

        input.submit(fn=submit, inputs=[input, chatbot], outputs=[input, chatbot])
        chatbot.flushed(fn=flushed, outputs=[input])

        demo.load(get_clue,
                  inputs=[],
                  outputs=clue_container,
                  every=0.5)
    demo.launch(share=True)
