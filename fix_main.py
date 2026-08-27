with open('app/src/main/java/com/titan/zapdial/MainActivity.kt', 'r') as f:
    content = f.read()

app_nav = """@Composable
fun AppNavigationContainer(intent: Intent?) {
    val callState by CallSessionManager.callState.collectAsState()
"""
content = content.replace("@Composable\nfun AppNavigationContainer() {", app_nav)

content = content.replace("AppNavigationContainer()", "AppNavigationContainer(intent)")

main_home = """@Composable
fun MainHomeScreen(startRoute: String) {
"""
content = content.replace("@Composable\nfun MainHomeScreen() {", main_home)

call_home_new = """    } else {
        val startRoute = intent?.getStringExtra("start_route") ?: "home"
        MainHomeScreen(startRoute)
    }"""
content = content.replace("""    } else {
        MainHomeScreen()
    }""", call_home_new)

content = content.replace('NavHost(navController, startDestination = "home")', 'NavHost(navController, startDestination = startRoute)')

with open('app/src/main/java/com/titan/zapdial/MainActivity.kt', 'w') as f:
    f.write(content)
