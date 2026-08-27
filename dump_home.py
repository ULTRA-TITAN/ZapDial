import sys
with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()
    
# Let's save it somewhere or print the number of lines
print(len(content.split('\n')))
