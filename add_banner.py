import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

banner_composable = """@Composable
fun DefaultDialerBanner() {
    val context = LocalContext.current
    val roleManager = context.getSystemService(Context.ROLE_SERVICE) as? android.app.role.RoleManager
    val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as? android.telecom.TelecomManager
    
    var isDefault by remember {
        mutableStateOf(
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.Q) {
                roleManager?.isRoleHeld(android.app.role.RoleManager.ROLE_DIALER) == true
            } else {
                telecomManager?.defaultDialerPackage == context.packageName
            }
        )
    }

    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { _ -> 
        isDefault = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.Q) {
            roleManager?.isRoleHeld(android.app.role.RoleManager.ROLE_DIALER) == true
        } else {
            telecomManager?.defaultDialerPackage == context.packageName
        }
    }

    if (!isDefault) {
        Card(
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = ColorFaintGreen),
            modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp).clickable {
                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.Q) {
                    val intent = roleManager?.createRequestRoleIntent(android.app.role.RoleManager.ROLE_DIALER)
                    if (intent != null) launcher.launch(intent)
                } else {
                    val intent = Intent(android.telecom.TelecomManager.ACTION_CHANGE_DEFAULT_DIALER)
                    intent.putExtra(android.telecom.TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME, context.packageName)
                    launcher.launch(intent)
                }
            }
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(imageVector = Icons.Default.Call, contentDescription = "Dialer", tint = ColorGreenSuccess)
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text("Set as Default Dialer", fontWeight = FontWeight.Bold, color = ColorPureBlack, fontSize = 16.sp)
                    Text("Required to make and receive calls", color = ColorSlateGray, fontSize = 14.sp)
                }
            }
        }
    }
}
"""

if "fun DefaultDialerBanner" not in content:
    content += "\n" + banner_composable

search_bar_invocation = """        item {
            SearchBarSection(
                query = searchQuery,
                onQueryChange = { searchQuery = it },
                onSettingsClick = { showSettings = true }
            )
            Spacer(modifier = Modifier.height(24.dp))
        }"""
        
search_bar_replacement = """        item {
            SearchBarSection(
                query = searchQuery,
                onQueryChange = { searchQuery = it },
                onSettingsClick = { showSettings = true }
            )
            Spacer(modifier = Modifier.height(16.dp))
            DefaultDialerBanner()
            Spacer(modifier = Modifier.height(8.dp))
        }"""
        
content = content.replace(search_bar_invocation, search_bar_replacement)

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
