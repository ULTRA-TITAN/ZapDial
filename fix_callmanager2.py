import re

with open("app/src/main/java/com/titan/zapdial/CallManager.kt", "r") as f:
    content = f.read()

new_logic = """
    fun initiateCallWithSimCheck(context: Context, number: String, showSimSelection: (List<PhoneAccountHandle>) -> Unit) {
        val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
        val defaultSimSlot = sharedPrefs.getInt("KEY_DEFAULT_SIM_SLOT", -1)
        val availableSims = getAvailableSims(context)
        
        if (availableSims.isEmpty()) {
            makeCall(context, number)
        } else if (availableSims.size == 1) {
            makeCall(context, number, availableSims[0])
        } else {
            if (defaultSimSlot == -1 || defaultSimSlot >= availableSims.size) {
                showSimSelection(availableSims)
            } else {
                makeCall(context, number, availableSims[defaultSimSlot])
            }
        }
    }

    fun makeCall"""

content = content.replace("    fun makeCall", new_logic)

with open("app/src/main/java/com/titan/zapdial/CallManager.kt", "w") as f:
    f.write(content)

