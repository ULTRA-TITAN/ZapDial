import re

with open("/app/applet/app/src/main/AndroidManifest.xml", "r") as f:
    content = f.read()

old_code = """        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.MyApplication">"""

new_code = """        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:showWhenLocked="true"
            android:turnScreenOn="true"
            android:theme="@style/Theme.MyApplication">"""

content = content.replace(old_code, new_code)

with open("/app/applet/app/src/main/AndroidManifest.xml", "w") as f:
    f.write(content)
