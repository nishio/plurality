"""
Tool to assist in fixing translation errors

"""

import json


cache = json.load(open("cache.json", "r", encoding="utf-8"))


def save():
    with open("cache.json", "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def print_pair(k):
    print(k)
    print("-" * 10)
    print(cache[k]["ja"])
    print()


last_results = []


def search_ja(keyword):
    last_results.clear()
    for k in cache:
        if cache[k]["latest"] == False:
            continue
        if keyword in cache[k]["ja"]:
            last_results.append(k)

    for k in last_results:
        print_pair(k)
    print(f"Found {len(last_results)} results")


def search_orig(keyword="數位"):
    last_results.clear()
    for k in cache:
        if cache[k]["latest"] == False:
            continue
        if keyword in k:
            last_results.append(k)

    for k in last_results:
        print_pair(k)
    print(f"Found {len(last_results)} results")


def edit_line(keyword):
    target = []
    for k in cache:
        if cache[k]["latest"] == False:
            continue
        if keyword in cache[k]["ja"]:
            target.append(k)

    if len(target) == 0:
        print("No match")
        return
    if len(target) > 1:
        for k in target:
            print_pair(k)

        print("Too many matches")
        return

    k = target[0]
    print_pair(k)
    new = input("New line: ")
    if new == "":
        print("cancelled")
        return
    cache[k]["ja"] = new
    save()
    print("saved")


def replace(keyword, new_keyword):
    """
    Find all lines that contains keyword, and replace it with new_keyword

    Sample Usage:
    replace("審議", "熟議")
    Found 37 matches
    view? (y/n)n
    replace? (y/n)y
    saved
    """
    target = []
    for k in cache:
        if cache[k]["latest"] == False:
            continue
        if keyword in cache[k]["ja"]:
            target.append(k)

    if len(target) == 0:
        print("No match")
        return

    print(f"Found {len(target)} matches")
    if input("view? (y/n)") == "y":
        for k in target:
            print_pair(k)

    if input("replace? (y/n)") == "y":
        for k in target:
            cache[k]["ja"] = cache[k]["ja"].replace(keyword, new_keyword)
        save()
        print("saved")
