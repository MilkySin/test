#!/usr/bin/env python3

import sys
import requests
import json


def get_name():
    username = input("Username: ")
    return username


def get_repo(username):
    repos: list[str] = []
    s = requests.get(f"https://api.github.com/users/{username}/repos")
    try:
        repos = [
            dic["full_name"][dic["full_name"].rfind("/") + 1 :]
            for dic in json.loads(s.text)
        ]
    except TypeError:
        print(f"User {username} doesn't exist")
    return repos


def main():
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = get_name()
    repos = get_repo(username)
    for i in repos:
        print(i)


if __name__ == "__main__":
    main()
