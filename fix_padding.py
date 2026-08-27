with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

content = content.replace(
    "PaddingValues(horizontal = 8.dp, bottom = 16.dp)", 
    "PaddingValues(start = 8.dp, top = 0.dp, end = 8.dp, bottom = 16.dp)"
)

content = content.replace(
    "Modifier.padding(horizontal = 8.dp, bottom = 16.dp)",
    "Modifier.padding(start = 8.dp, top = 0.dp, end = 8.dp, bottom = 16.dp)"
)

content = content.replace(
    "Modifier.padding(start = 8.dp, top = 8.dp, bottom = 16.dp)",
    "Modifier.padding(start = 8.dp, top = 8.dp, end = 0.dp, bottom = 16.dp)"
)

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
