"""
Auto-translation from English/Traditional Mandarin to Japanese

Previous translation is cached in cache.json.

MIT License / 2023 NISHIO Hirokazu
"""
import os
import dotenv
import openai
import json
import argparse

# assure the script runs in root/autotrans
if not os.getcwd().endswith("autotrans"):
    os.chdir("autotrans")


dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

parser = argparse.ArgumentParser()
parser.add_argument(
    "--skip-gpt",
    action="store_true",
    help="skip GPT API call for tests",
)
parser.add_argument(
    "--target",
    action="store",
    default="all",
    help="target file to translate",
)
args = parser.parse_args()


# load previoud translation cache
if os.path.exists("cache.json"):
    prev_trans = json.load(open("cache.json", "r", encoding="utf-8"))
else:
    prev_trans = {}


## CACHE CONTROL
# new_trans = {}  # clear not-used cache
# new_trans = prev_trans.copy()  # keep not-used cache
# mark all cache as not latest, then add new one as latest
new_trans = prev_trans.copy()
for k in new_trans:
    new_trans[k]["latest"] = False


def generate_system_prompt(line):
    return """\
# Task
Translate given input text to Japanese. The input is a line from a markdown file.

# Input
{line}

# Output
""".format(
        line=line
    )


def call_gpt(prompt, model="gpt-3.5-turbo"):
    print("# Call GPT")
    print("## Prompt")
    print(prompt)
    if args.skip_gpt:
        print("## Skipped")
        return ["GPT Skipped"]
    print("--- End of Prompt")

    messages = [{"role": "system", "content": prompt}]
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.0,
            # max_tokens=max_tokens,
            n=1,
            stop=None,
        )
        ret = response.choices[0].message.content.strip()
        print("## GPT Response")
        print(ret)
        print("--- End of GPT Response")
    except Exception as e:
        print("## GPT Error")
        print(e)
        return ""
    return ret


def translate_one_line(
    line="網際網路揭開世界面紗，是光引向前行道路。理想與變革的 60 年代，見證了跨文化技術的萌芽，催生超越地理和時間限制的數位社群。通過這座數位橋樑，知識在不同語文間綻放。",
):
    line = line.rstrip("\n")  # remove trailing newline
    if line.strip() == "":
        return line
    if line in prev_trans:
        ret = prev_trans[line]["ja"]
    else:
        prompt = generate_system_prompt(line)
        ret = call_gpt(prompt)
    line = line.rstrip("\n")  # remove trailing newline
    new_trans[line] = {"ja": ret}
    return ret


def translate_one_page(page="../contents/traditional-mandarin/01-數位觀照.md"):
    print("Translating page: " + page)
    basename = os.path.basename(page)
    OUTFILE = f"../contents/japanese-auto/{basename}"

    with open(page, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        r = translate_one_line(line)
        new_lines.append(r)

    with open(OUTFILE, "w", encoding="utf-8") as f:
        for line in new_lines:
            f.write(line + "\n")

    # add language icon
    OUTFILE = f"../contents/japanese-auto/with_lang_icon/{basename}"
    if "traditional-mandarin" in page:
        icon = "🇹🇼"
    else:
        icon = "🇺🇸"
    with open(OUTFILE, "w", encoding="utf-8") as f:
        for line in new_lines:
            if line:
                f.write(f"{icon}{line}\n")
            else:
                f.write("\n")


def main():
    # translate all pages
    targets = [
        f"../contents/english/{f}" for f in os.listdir("../contents/english")
    ] + [
        f"../contents/traditional-mandarin/{f}"
        for f in os.listdir("../contents/traditional-mandarin")
    ]
    targets.sort()
    for page in targets:
        translate_one_page(page)
        # save translation cache
        with open("cache.json", "w", encoding="utf-8") as f:
            json.dump(new_trans, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
