import re
import os

files = [
    "app/src/main/java/com/titan/zapdial/HomeScreen.kt",
    "app/src/main/java/com/titan/zapdial/ContactsScreen.kt"
]

for file in files:
    with open(file, "r") as f:
        content = f.read()
    
    # Update PageBackground
    content = re.sub(r'val PageBackground = Color\(0xFFFDFCFA\)', r'val PageBackground = Color(0xFFFFFFFF)', content)
    # Update TextPrimary
    content = re.sub(r'val TextPrimary = Color\(0xFF2A2A2E\)', r'val TextPrimary = Color(0xFF0F172A)', content)
    # Update TextSecondary
    content = re.sub(r'val TextSecondary = Color\(0xFF9A9AA2\)', r'val TextSecondary = Color(0xFF64748B)', content)
    
    with open(file, "w") as f:
        f.write(content)

