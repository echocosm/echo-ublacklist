CUSTOM = "echo-custom.txt"
STITCHED = "stitcher-output.txt"
OUTPUT = "echo-ublacklist.txt"

with open(CUSTOM, encoding="utf-8") as f:
    custom = f.read()

with open(STITCHED, encoding="utf-8") as f:
    stitched = f.read()

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("# echo ------------------------------------------------------------------------------------------------------ START OF CUSTOM\n\n")
    f.write(custom)
    f.write("# echo ------------------------------------------------------------------------------------------------------ END OF CUSTOM\n")
    f.write("\n")
    f.write(stitched)

print(f"Done! Created {OUTPUT}")