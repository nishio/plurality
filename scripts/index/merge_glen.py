glen_lines = open("index_by_glen.txt", "r").readlines()
used = {}
for line in glen_lines:
    used[line] = False

# read index_for_copyedit.md
lines = open("index_for_copyedit.md", "r").readlines()
with open("merged_index_for_copyedit.md", "w") as f:
    for line in lines:
        for gline in glen_lines:
            if line.lower() == gline.lower():
                used[gline] = True
                print(gline.strip(), file=f)
                break
        else:
            print(line.strip(), file=f)

for line in glen_lines:
    if not used.get(line, True):
        print(line.strip())
