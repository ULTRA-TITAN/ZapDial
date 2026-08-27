with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

content = content.replace("context.startActivity(intent)", "try { context.startActivity(intent) } catch(e: Exception) {}")

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
