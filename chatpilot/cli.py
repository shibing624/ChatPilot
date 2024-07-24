# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: Cli for chatpilot
"""
import argparse

from .langchain_assistant import LangchainAssistant
from .config import OPENAI_API_KEY, OPENAI_API_BASE


def main():
    parser = argparse.ArgumentParser(description='chatpilot cli')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo-1106', help='openai model name')
    parser.add_argument('--search', type=str, default='duckduckgo', help='search engine name, e.g. duckduckgo, serper')
    parser.add_argument('--openai_api_key', type=str, default=OPENAI_API_KEY, help='openai api key')
    parser.add_argument('--openai_api_base', type=str, default=OPENAI_API_BASE, help='openai api base url')
    args = parser.parse_args()

    m = LangchainAssistant(
        model_api_key=args.openai_api_key,
        model_api_base=args.openai_api_base,
        model_type='openai',
        model_name=args.model,
        search_engine_name=args.search,
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
