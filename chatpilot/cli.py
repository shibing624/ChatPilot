# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: Cli for chatpilot
"""
import argparse
import sys

sys.path.append('..')
from chatpilot import ChatAgent, OPENAI_API_KEY, OPENAI_API_BASE, SERPER_API_KEY


def main():
    parser = argparse.ArgumentParser(description='chatpilot cli')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo-1106', help='openai model name')
    parser.add_argument('--search', type=str, default='duckduckgo', help='search engine name, e.g. duckduckgo, serper')
    parser.add_argument('--openai_api_key', type=str, default=OPENAI_API_KEY, help='openai api key')
    parser.add_argument('--openai_api_base', type=str, default=OPENAI_API_BASE, help='openai api base url')
    parser.add_argument('--serper_api_key', type=str, default=SERPER_API_KEY, help='serper api key')
    args = parser.parse_args()

    m = ChatAgent(
        openai_model=args.model,
        search_engine_name=args.search,
        openai_api_bases=args.openai_api_base,
        openai_api_keys=args.openai_api_key,
        serper_api_key=args.serper_api_key
    )

    def get_llm_response(query):
        r = m.run(query)
        return r.get('output', '')

    print("Welcome to ChatPilot! please input User question, Type 'exit' to end the conversation.")
    while True:
        user_question = input("User: ")
        user_question = user_question.strip()
        if user_question == 'exit':
            break
        output = get_llm_response(user_question)
        print(output)


if __name__ == "__main__":
    main()
