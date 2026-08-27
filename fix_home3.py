with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    lines = f.readlines()

new_lines = []
view_count = 0
in_call_history = False

for line in lines:
    if "fun CallHistoryItemCard" in line:
        in_call_history = True
        view_count = 0
        
    if "val view = LocalView.current" in line and in_call_history:
        view_count += 1
        if view_count > 1:
            continue # skip the second one
            
    new_lines.append(line)

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.writelines(new_lines)
