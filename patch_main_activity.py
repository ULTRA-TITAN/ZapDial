import re

with open("app/src/main/java/com/titan/zapdial/MainActivity.kt", "r") as f:
    content = f.read()

old_on_create = """    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {"""

new_on_create = """    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O_MR1) {
            setShowWhenLocked(true)
            setTurnScreenOn(true)
        } else {
            @Suppress("DEPRECATION")
            window.addFlags(
                android.view.WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or
                android.view.WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON or
                android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON
            )
        }
        setContent {"""

if "setShowWhenLocked" not in content:
    content = content.replace(old_on_create, new_on_create)

with open("app/src/main/java/com/titan/zapdial/MainActivity.kt", "w") as f:
    f.write(content)
