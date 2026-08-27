import re
with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

content = content.replace("it.phoneNumber !hiddenFavorites.contains(it.phoneNumber)", "!hiddenFavorites.contains(it.phoneNumber)")

# Fix double view declaration
content = re.sub(r'val view = LocalView\.current\s+val view = LocalView\.current', 'val view = LocalView.current', content)

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
