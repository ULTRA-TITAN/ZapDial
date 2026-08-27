import re

with open('app/src/main/java/com/titan/zapdial/MainActivity.kt', 'r') as f:
    content = f.read()

content = content.replace("""    }
    val context = LocalContext.current
    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)""", """    }
    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)""")

with open('app/src/main/java/com/titan/zapdial/MainActivity.kt', 'w') as f:
    f.write(content)
