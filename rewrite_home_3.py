with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

content = content.replace("items(filteredHistory, key = { it.id }) { call ->", "itemsIndexed(filteredHistory, key = { index, call -> \"${call.id}_${index}\" }) { _, call ->")

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
