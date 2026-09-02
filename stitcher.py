import requests

INPUT = "rules-list.txt"
OUTPUT = "stitcher-output.txt"

with open(INPUT, encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

with open(OUTPUT, "w", encoding="utf-8") as out:
    for url in urls:
        print(f"Downloading: {url}")

        response = requests.get(url)
        response.raise_for_status()

        lines = response.text.splitlines()

        for i, line in enumerate(lines):
            if line.strip().startswith("name:"):
                lines[i] = "#" + line
                break

        out.write("\n".join(lines))
        out.write("\n\n")

print(f"\nDone! Created {OUTPUT}")