import requests
import json
import sys
import html


def GetPost(top_N: int, label: str):
    ses = requests.Session()
    req = ses.get(
        f"https://api.stackexchange.com/2.3/questions?page=1&pagesize={top_N}&order=desc&sort=votes&tagged={label}&site=stackoverflow",
        timeout=15,
    )
    info = json.loads(req.content)
    return info


def GetTopAnswer(question_id):
    ses = requests.Session()
    req = ses.get(
        f"https://api.stackexchange.com/2.3/questions/{question_id}/answers?page=1&pagesize=1&order=desc&sort=votes&site=stackoverflow",
        timeout=15,
    )
    top_post = json.loads(req.content)
    return top_post


def GetPostInfo(items):
    post_title = items["title"]
    post_name = items["owner"]["display_name"]
    post_id = items["question_id"]
    post_link = items["link"]
    return post_title, post_name, post_id, post_link


def GetAnswerInfo(items):
    answer_id = items["answer_id"]
    return answer_id


def main():
    top_N = sys.argv[1]
    label = sys.argv[2]
    top_post = GetPost(top_N, label)
    for question in top_post["items"]:
        post_title, post_name, post_id, post_link = GetPostInfo(question)
        top_answer = GetTopAnswer(post_id)
        for top_answer in top_answer["items"]:
            answer_id = GetAnswerInfo(top_answer)
            answer_link = f"{post_link}/{answer_id}#{answer_id}"
        print(
            f"Post Title: {html.unescape(post_title)} | Post name : {post_name} | Top Answer: {answer_link}"
        )


if __name__ == "__main__":
    main()
