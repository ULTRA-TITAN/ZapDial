import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

# Make sure we have the required imports
imports_to_add = """
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Search
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
"""
if "import androidx.compose.material.icons.filled.Settings" not in content:
    content = content.replace("import androidx.compose.material3.*", "import androidx.compose.material3.*\n" + imports_to_add)

# State for history sheet
history_state = """
    var showFrequentContacts by remember {
        mutableStateOf(sharedPrefs.getBoolean("KEY_SHOW_FREQUENT", true))
    }
    var selectedHistoryContact by remember { mutableStateOf<String?>(null) }
"""

content = content.replace("    var hasCallLogPermission by remember {", history_state + "\n    var hasCallLogPermission by remember {")

# Search Bar Section and Frequent Contacts Section
search_bar = """
            item {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 16.dp)
                        .clip(RoundedCornerShape(32.dp))
                        .background(Color.White)
                        .padding(horizontal = 8.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(Icons.Default.Settings, contentDescription = "Settings", tint = TextSecondary)
                    }
                    
                    Box(modifier = Modifier.weight(1f).padding(horizontal = 8.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Search, contentDescription = "Search", tint = TextSecondary)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Search contacts", color = TextSecondary, fontSize = 16.sp)
                        }
                    }

                    IconButton(onClick = { /* Voice Search */ }) {
                        Icon(Icons.Default.Mic, contentDescription = "Voice Search", tint = TextSecondary)
                    }
                }
            }
            
            if (showFrequentContacts) {
                item {
                    Text(
                        text = "Favorites",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Medium,
                        color = TextPrimary,
                        modifier = Modifier.padding(bottom = 12.dp, start = 8.dp)
                    )
                }
                
                item {
                    val frequent = allContacts.take(8)
                    if (frequent.isNotEmpty()) {
                        LazyRow(
                            horizontalArrangement = Arrangement.spacedBy(16.dp),
                            contentPadding = PaddingValues(horizontal = 8.dp, bottom = 16.dp)
                        ) {
                            items(frequent) { contact ->
                                Column(
                                    horizontalAlignment = Alignment.CenterHorizontally,
                                    modifier = Modifier.clickable {
                                        if (mistouchPrevention) {
                                            // Handling in ContactCard directly or CallManager
                                        } else {
                                            CallManager.makeCall(context, contact.phoneNumber)
                                        }
                                    }
                                ) {
                                    Avatar(name = contact.name, size = 56.dp)
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        text = contact.name.split(" ").firstOrNull() ?: "",
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = TextPrimary,
                                        maxLines = 1,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                }
                            }
                        }
                    } else {
                        Text(
                            text = "No favorites yet.",
                            fontSize = 14.sp,
                            color = TextSecondary,
                            modifier = Modifier.padding(horizontal = 8.dp, bottom = 16.dp)
                        )
                    }
                }
            }
"""

# Find where Recents title is added and replace it with search bar and favorites
old_recents = """
            item {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Recents", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(Icons.Default.Edit, contentDescription = "Settings", tint = TextPrimary)
                    }
                }
            }
"""

new_recents = search_bar + """
            item {
                Text(
                    "Recents", 
                    fontSize = 28.sp, 
                    fontWeight = FontWeight.Bold, 
                    color = TextPrimary,
                    modifier = Modifier.padding(start = 8.dp, top = 8.dp, bottom = 16.dp)
                )
            }
"""
content = content.replace(old_recents, new_recents)

# Pass onViewHistory to CallHistoryItemCard
old_card_call = """
                            CallHistoryItemCard(
                                item = call, 
                                mistouchPrevention = mistouchPrevention,
                                onDelete = { deletedItem ->
"""
new_card_call = """
                            CallHistoryItemCard(
                                item = call, 
                                mistouchPrevention = mistouchPrevention,
                                onViewHistory = { selectedHistoryContact = call.number },
                                onDelete = { deletedItem ->
"""
content = content.replace(old_card_call, new_card_call)

# Add Bottom sheet state
sheet_state_code = """
        SnackbarHost(
            hostState = snackbarHostState,
            modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 64.dp)
        )
        
        if (selectedHistoryContact != null) {
            ModalBottomSheet(
                onDismissRequest = { selectedHistoryContact = null },
                containerColor = PageBackground,
                shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp)
            ) {
                Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp, vertical = 16.dp).padding(bottom = 48.dp)) {
                    val matchingCalls = callHistory.filter { it.number == selectedHistoryContact }
                    val name = matchingCalls.firstOrNull()?.name ?: selectedHistoryContact ?: "Unknown"
                    
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Avatar(name = name, size = 56.dp)
                        Spacer(modifier = Modifier.width(16.dp))
                        Column {
                            Text(name, fontSize = 22.sp, fontWeight = FontWeight.SemiBold, color = TextPrimary)
                            Text(selectedHistoryContact ?: "", fontSize = 15.sp, color = TextSecondary)
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(24.dp))
                    Text("Recent Calls", fontSize = 16.sp, fontWeight = FontWeight.Medium, color = TextPrimary)
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    LazyColumn(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                        items(matchingCalls) { call ->
                            val isMissed = call.type == CallLog.Calls.MISSED_TYPE
                            val relativeTime = DateUtils.getRelativeTimeSpanString(
                                call.date, System.currentTimeMillis(), DateUtils.MINUTE_IN_MILLIS
                            ).toString()
                            
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                val icon = when (call.type) {
                                    CallLog.Calls.INCOMING_TYPE -> Icons.AutoMirrored.Filled.CallReceived
                                    CallLog.Calls.MISSED_TYPE -> Icons.AutoMirrored.Filled.CallMissed
                                    else -> Icons.AutoMirrored.Filled.CallMade
                                }
                                Icon(icon, contentDescription = null, tint = if (isMissed) ColorRedMissed else TextSecondary, modifier = Modifier.size(20.dp))
                                Spacer(modifier = Modifier.width(12.dp))
                                Column {
                                    Text(
                                        when (call.type) {
                                            CallLog.Calls.INCOMING_TYPE -> "Incoming Call"
                                            CallLog.Calls.MISSED_TYPE -> "Missed Call"
                                            else -> "Outgoing Call"
                                        },
                                        fontSize = 15.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = if (isMissed) ColorRedMissed else TextPrimary
                                    )
                                    Text("$relativeTime • ${call.simName}", fontSize = 13.sp, color = TextSecondary)
                                }
                                Spacer(modifier = Modifier.weight(1f))
                                val minutes = call.duration / 60
                                val seconds = call.duration % 60
                                val durationStr = if (minutes > 0) "${minutes}m ${seconds}s" else "${seconds}s"
                                Text(durationStr, fontSize = 13.sp, color = TextSecondary)
                            }
                        }
                    }
                }
            }
        }
"""
content = content.replace("""        SnackbarHost(
            hostState = snackbarHostState,
            modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 64.dp)
        )
""", sheet_state_code)


# Update CallHistoryItemCard signature and button
old_card_sig = """fun CallHistoryItemCard(
    item: HomeCallItem, 
    mistouchPrevention: Boolean,
    onDelete: (HomeCallItem) -> Unit
) {"""
new_card_sig = """fun CallHistoryItemCard(
    item: HomeCallItem, 
    mistouchPrevention: Boolean,
    onViewHistory: () -> Unit = {},
    onDelete: (HomeCallItem) -> Unit
) {"""
content = content.replace(old_card_sig, new_card_sig)

old_view_history = """                    OutlinedButton(
                        onClick = { /* View history omitted for simplicity */ },"""
new_view_history = """                    OutlinedButton(
                        onClick = onViewHistory,"""
content = content.replace(old_view_history, new_view_history)


with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
