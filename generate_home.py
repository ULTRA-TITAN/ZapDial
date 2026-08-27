def generate():
    code = """package com.titan.zapdial

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.provider.CallLog
import android.provider.ContactsContract
import android.telephony.TelephonyManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.CallMade
import androidx.compose.material.icons.automirrored.filled.CallMissed
import androidx.compose.material.icons.automirrored.filled.CallReceived
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.History
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlin.math.absoluteValue
import android.text.format.DateUtils

private val PageBackground = Color(0xFFFDFCFA)
private val PlateBackground = Color(0xFFFFFFFF)
private val TextPrimary = Color(0xFF2A2A2E)
private val TextSecondary = Color(0xFF9A9AA2)
private val ColorRedMissed = Color(0xFFB3574F)
private val ColorGreenSuccess = Color(0xFF4C8B62)
private val AvatarPalette = listOf(
    Color(0xFFAFC4E0), Color(0xFFAECBB8), Color(0xFFE0B3AE), Color(0xFFC9BEE0),
    Color(0xFFE0B8CB), Color(0xFFE0CBA6), Color(0xFFA9CFC9), Color(0xFFC7C7CE)
)

fun getAvatarColor(name: String): Color {
    if (name.isBlank()) return AvatarPalette.last()
    val hash = name.hashCode().absoluteValue
    return AvatarPalette[hash % AvatarPalette.size]
}

fun getCategoryForDate(dateInMillis: Long): String {
    val now = System.currentTimeMillis()
    val diff = now - dateInMillis
    val day = 24 * 60 * 60 * 1000L
    return when {
        diff < day -> "Today"
        diff < 2 * day -> "Yesterday"
        diff < 30 * day -> "This Month"
        else -> "Older"
    }
}

data class HomeCallItem(
    val id: String,
    val number: String,
    val name: String?,
    val type: Int,
    val date: Long,
    val duration: Long,
    val location: String,
    val simName: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(onNavigateToSettings: () -> Unit = {}) {
    val context = LocalContext.current
    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var mistouchPrevention by remember {
        mutableStateOf(sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false))
    }
    var callHistory by remember { mutableStateOf<List<HomeCallItem>>(emptyList()) }
    var allContacts by remember { mutableStateOf<List<Contact>>(emptyList()) }
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()
    var hasCallLogPermission by remember {
        mutableStateOf(ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CALL_LOG) == PackageManager.PERMISSION_GRANTED)
    }

    val tm = context.getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
    val carrierName = tm.networkOperatorName.takeIf { it.isNotBlank() } ?: "Network"
    val country = tm.networkCountryIso.uppercase()
    val defaultLocation = if (country.isNotBlank()) "$carrierName • $country" else carrierName

    val callLogPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        hasCallLogPermission = isGranted
        if (isGranted) {
            coroutineScope.launch {
                callHistory = CallLogFetcher.fetchCallHistory(context, defaultLocation, allContacts)
            }
        }
    }

    LaunchedEffect(hasCallLogPermission, allContacts) {
        if (hasCallLogPermission) {
            callHistory = CallLogFetcher.fetchCallHistory(context, defaultLocation, allContacts)
        }
    }

    LaunchedEffect(Unit) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) == PackageManager.PERMISSION_GRANTED) {
            allContacts = ContactFetcher.fetchContacts(context)
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .background(PageBackground)
                .padding(horizontal = 16.dp),
            contentPadding = PaddingValues(vertical = 16.dp)
        ) {
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

            if (hasCallLogPermission) {
                val groupedHistory = callHistory.groupBy { getCategoryForDate(it.date) }
                val categories = listOf("Today", "Yesterday", "This Month", "Older")
                categories.forEach { category ->
                    val calls = groupedHistory[category]
                    if (!calls.isNullOrEmpty()) {
                        item {
                            Text(
                                text = category,
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Medium,
                                color = TextPrimary,
                                modifier = Modifier.padding(top = 16.dp, bottom = 12.dp, start = 8.dp)
                            )
                        }
                        itemsIndexed(calls, key = { index, call -> "${call.id}_${index}" }) { _, call ->
                            CallHistoryItemCard(
                                item = call, 
                                mistouchPrevention = mistouchPrevention,
                                onDelete = { deletedItem ->
                                    val previousHistory = callHistory
                                    callHistory = callHistory.filter { it.id != deletedItem.id }
                                    coroutineScope.launch {
                                        val result = snackbarHostState.showSnackbar(
                                            message = "Call log deleted",
                                            actionLabel = "UNDO",
                                            duration = SnackbarDuration.Short
                                        )
                                        if (result == SnackbarResult.ActionPerformed) {
                                            callHistory = previousHistory
                                        } else {
                                            GlobalScope.launch(Dispatchers.IO) {
                                                try {
                                                    context.contentResolver.delete(
                                                        CallLog.Calls.CONTENT_URI,
                                                        "${CallLog.Calls._ID} = ?",
                                                        arrayOf(deletedItem.id)
                                                    )
                                                } catch (e: Exception) {
                                                    e.printStackTrace()
                                                }
                                            }
                                        }
                                    }
                                }
                            )
                            Spacer(modifier = Modifier.height(10.dp))
                        }
                    }
                }
            } else {
                item {
                    Column(
                        modifier = Modifier.fillMaxWidth().padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text("No Call Logs Permission", fontSize = 16.sp, color = TextSecondary)
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = { callLogPermissionLauncher.launch(Manifest.permission.READ_CALL_LOG) }) {
                            Text("Grant")
                        }
                    }
                }
            }
        }
        SnackbarHost(
            hostState = snackbarHostState,
            modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 64.dp)
        )
    }
}

@Composable
fun CallHistoryItemCard(
    item: HomeCallItem, 
    mistouchPrevention: Boolean,
    onDelete: (HomeCallItem) -> Unit
) {
    val context = LocalContext.current
    var expanded by remember { mutableStateOf(false) }
    var callToConfirm by remember { mutableStateOf<String?>(null) }
    val view = LocalView.current
    
    val callPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            if (mistouchPrevention) callToConfirm = item.number else CallManager.makeCall(context, item.number)
        }
    }
    
    callToConfirm?.let { num ->
        CallConfirmationDialog(
            name = item.name,
            number = num,
            onConfirm = { CallManager.makeCall(context, num) },
            onDismiss = { callToConfirm = null }
        )
    }
    
    val displayName = item.name ?: item.number
    val relativeTime = DateUtils.getRelativeTimeSpanString(
        item.date, System.currentTimeMillis(), DateUtils.MINUTE_IN_MILLIS
    ).toString()
    
    val isMissed = item.type == CallLog.Calls.MISSED_TYPE
    val statusColor = if (isMissed) ColorRedMissed else TextSecondary
    
    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = PlateBackground),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
        modifier = Modifier
            .fillMaxWidth()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { expanded = !expanded },
                    onLongPress = { 
                        view.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS)
                        onDelete(item)
                    }
                )
            }
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier.size(50.dp).clip(CircleShape).background(getAvatarColor(displayName))
                ) {
                    Text(
                        text = displayName.take(1).uppercase(),
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color.White
                    )
                }
                Spacer(modifier = Modifier.width(16.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = displayName,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Normal,
                        color = if (isMissed) ColorRedMissed else TextPrimary,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    
                    Spacer(modifier = Modifier.height(3.dp))
                    
                    Text(
                        text = "${item.location} • $relativeTime",
                        fontSize = 13.sp,
                        color = TextSecondary,
                        fontWeight = FontWeight.Light
                    )
                    
                    Spacer(modifier = Modifier.height(3.dp))
                    
                    Text(
                        text = item.simName,
                        fontSize = 13.sp,
                        color = TextSecondary,
                        fontWeight = FontWeight.Light
                    )
                }
                
                IconButton(onClick = {
                    if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                        if (mistouchPrevention) callToConfirm = item.number else CallManager.makeCall(context, item.number)
                    } else {
                        callPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
                    }
                }) {
                    Icon(Icons.Default.Call, contentDescription = "Call", tint = ColorGreenSuccess)
                }
            }

            AnimatedVisibility(visible = expanded) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color(0xFFFAFAF9))
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = { /* View history omitted for simplicity */ },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = TextPrimary),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Default.History, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(12.dp))
                        Text("View Call History", fontSize = 15.sp, fontWeight = FontWeight.Medium)
                    }
                    OutlinedButton(
                        onClick = {
                            val intent = Intent(Intent.ACTION_INSERT_OR_EDIT).apply {
                                type = ContactsContract.Contacts.CONTENT_ITEM_TYPE
                                putExtra(android.provider.ContactsContract.Intents.Insert.PHONE, item.number)
                            }
                            try { context.startActivity(intent) } catch(e: Exception) {}
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = TextPrimary),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Default.Edit, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(if (item.name == null) "Add Contact" else "Edit Contact", fontSize = 15.sp, fontWeight = FontWeight.Medium)
                    }
                }
            }
        }
    }
}
"""
    with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
        f.write(code)

generate()
