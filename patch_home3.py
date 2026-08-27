with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

content = content.replace("    Box\n        LazyColumn(", "    Box(modifier = Modifier.fillMaxSize()) {\n        LazyColumn(")

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
