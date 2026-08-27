with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    lines = f.readlines()

# Find the end of LazyColumn, which is before SnackbarHost
insert_idx = -1
for i, line in enumerate(lines):
    if "SnackbarHost(" in line:
        insert_idx = i
        break

if insert_idx != -1:
    lines.insert(insert_idx - 1, "            }\n") # close else block

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.writelines(lines)
