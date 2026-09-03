INPUT = "echo-ublacklist.txt"

with open(INPUT, encoding="utf-8") as f:
    lines = f.readlines()

seen = set()
output = []

for line in lines:
    if line not in seen:
        seen.add(line)
        output.append(line)

with open(INPUT, "w", encoding="utf-8") as f:
    f.writelines(output)

removed = len(lines) - len(output)

print(f"Done! Removed {removed} duplicate lines.")