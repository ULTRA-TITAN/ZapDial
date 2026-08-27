with open('app/src/main/java/com/titan/zapdial/ZapCallService.kt', 'r') as f:
    content = f.read()

on_call_added = """    override fun onCallAdded(call: Call) {
        super.onCallAdded(call)
        CallSessionManager.allCalls.value = calls"""
content = content.replace("""    override fun onCallAdded(call: Call) {
        super.onCallAdded(call)""", on_call_added)

on_call_removed = """    override fun onCallRemoved(call: Call) {
        super.onCallRemoved(call)
        CallSessionManager.allCalls.value = calls"""
content = content.replace("""    override fun onCallRemoved(call: Call) {
        super.onCallRemoved(call)""", on_call_removed)

with open('app/src/main/java/com/titan/zapdial/ZapCallService.kt', 'w') as f:
    f.write(content)
