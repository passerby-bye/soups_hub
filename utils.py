from enum import Enum


class AnswerState(Enum):
    CORRECT = 1
    WRONG = 2
    UNRELATED = 3
    KEY = 4
    SYSTEM_ERROR = 5

def map_response_to_answer_state(response):
    map = {"是": AnswerState.CORRECT, "恭喜你猜对了线索":AnswerState.KEY,"否": AnswerState.WRONG, "不相关": AnswerState.UNRELATED}
    print("agent response: ", response)
    for k,v in map.items():
        if k in response.content:
            return v
    return AnswerState.SYSTEM_ERROR


def check_keywords(answer, keywords, triggered_keywords):
    flag = 0
    for keyword in keywords:
        # 如果关键词在回答中出现，则将其添加到已触发的关键词集合中
        if keyword in answer:
            old = len(triggered_keywords) 
            triggered_keywords.add(keyword)
            if old != len(triggered_keywords):
                flag = 1

    # 如果已触发的关键词数量等于关键词总数，则返回True，否则返回False
    return len(triggered_keywords) == 3, triggered_keywords, flag


