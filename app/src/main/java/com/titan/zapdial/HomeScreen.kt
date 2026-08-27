package com.titan.zapdial

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
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.combinedClickable
import android.view.HapticFeedbackConstants
import androidx.compose.foundation.border
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
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.ui.text.TextStyle

import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Delete
import android.content.ClipboardManager
import android.content.ClipData
import android.widget.Toast
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Search
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items

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

private val PageBackground = Color(0xFFFFFFFF)
private val PlateBackground = Color(0xFFFFFFFF)
private val TextPrimary = Color(0xFF0F172A)
private val TextSecondary = Color(0xFF64748B)
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

@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)
@Composable
fun HomeScreen(onNavigateToSettings: () -> Unit = {}) {
    val context = LocalContext.current
    val view = LocalView.current
    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var mistouchPrevention by remember {
        mutableStateOf(sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false))
    }
    var callHistory by remember { mutableStateOf<List<HomeCallItem>>(emptyList()) }
    var allContacts by remember { mutableStateOf<List<Contact>>(emptyList()) }
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()

    var showFrequentContacts by remember {
        mutableStateOf(sharedPrefs.getBoolean("KEY_SHOW_FREQUENT", true))
    }
    var selectedHistoryContact by remember { mutableStateOf<String?>(null) }
    var searchQuery by remember { mutableStateOf("") }
    val favoriteNumbers = remember { mutableStateListOf<String>() }
    
    LaunchedEffect(Unit) {
        val favs = sharedPrefs.getStringSet("KEY_FAVORITES", emptySet()) ?: emptySet()
        favoriteNumbers.addAll(favs)
    }
    var callToConfirm by remember { mutableStateOf<Pair<String, String>?>(null) }

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


    val voiceSearchLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == android.app.Activity.RESULT_OK) {
            val matches = result.data?.getStringArrayListExtra(android.speech.RecognizerIntent.EXTRA_RESULTS)
            if (!matches.isNullOrEmpty()) {
                searchQuery = matches[0]
            }
        }
    }
    
    val audioPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            val intent = Intent(android.speech.RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE_MODEL, android.speech.RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            }
            try { voiceSearchLauncher.launch(intent) } catch (e: Exception) {}
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

    callToConfirm?.let { (name, number) ->
        CallConfirmationDialog(
            name = name,
            number = number,
            onConfirm = { CallManager.makeCall(context, number) },
            onDismiss = { callToConfirm = null }
        )
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
                    
                    Box(modifier = Modifier
                        .weight(1f)
                        .padding(horizontal = 8.dp),
                        contentAlignment = Alignment.CenterStart
                    ) {
                        if (searchQuery.isEmpty()) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.Search, contentDescription = "Search", tint = TextSecondary)
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("Search contacts", color = TextSecondary, fontSize = 16.sp)
                            }
                        } else {
                            Icon(Icons.Default.Search, contentDescription = "Search", tint = TextPrimary)
                        }
                        
                        BasicTextField(
                            value = searchQuery,
                            onValueChange = { searchQuery = it },
                            modifier = Modifier.fillMaxWidth().padding(start = 32.dp),
                            textStyle = TextStyle(fontSize = 16.sp, color = TextPrimary),
                            singleLine = true
                        )
                    }

                    IconButton(onClick = {
                        if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                            val intent = Intent(android.speech.RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                                putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE_MODEL, android.speech.RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                            }
                            try { voiceSearchLauncher.launch(intent) } catch (e: Exception) {}
                        } else {
                            audioPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                        }
                    }) {
                        Icon(Icons.Default.Mic, contentDescription = "Voice Search", tint = TextSecondary)
                    }
                }
            }
            
            if (searchQuery.isNotEmpty()) {
                val searchResults = allContacts.filter {
                    it.name.contains(searchQuery, ignoreCase = true) || it.phoneNumber.contains(searchQuery)
                }
                
                if (searchResults.isEmpty()) {
                    item {
                        Text(
                            text = "No contacts found.",
                            fontSize = 14.sp,
                            color = TextSecondary,
                            modifier = Modifier.padding(16.dp)
                        )
                    }
                } else {
                    items(searchResults) { contact ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    if (mistouchPrevention) {
                                        callToConfirm = Pair(contact.name, contact.phoneNumber)
                                    } else {
                                        CallManager.makeCall(context, contact.phoneNumber)
                                    }
                                }
                                .padding(vertical = 12.dp, horizontal = 8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Avatar(name = contact.name, size = 50.dp)
                            Spacer(modifier = Modifier.width(16.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = contact.name,
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = TextPrimary
                                )
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = contact.phoneNumber,
                                    fontSize = 14.sp,
                                    color = TextSecondary
                                )
                            }
                        }
                    }
                }
            } else {
            
            if (showFrequentContacts) {
                item {
                    var showContactPicker by remember { mutableStateOf(false) }
                    if (showContactPicker) {
                        ModalBottomSheet(onDismissRequest = { showContactPicker = false }, containerColor = PageBackground) {
                            LazyColumn(modifier = Modifier.fillMaxWidth().padding(16.dp).padding(bottom = 32.dp)) {
                                item {
                                    Text("Select a Favorite", fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 16.dp))
                                }
                                items(allContacts) { contact ->
                                    Row(modifier = Modifier.fillMaxWidth().clickable {
                                        if (!favoriteNumbers.contains(contact.phoneNumber)) {
                                            favoriteNumbers.add(contact.phoneNumber)
                                            sharedPrefs.edit().putStringSet("KEY_FAVORITES", favoriteNumbers.toSet()).apply()
                                        }
                                        showContactPicker = false
                                    }.padding(vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
                                        Avatar(name = contact.name, size = 40.dp)
                                        Spacer(modifier = Modifier.width(16.dp))
                                        Text(contact.name, fontSize = 16.sp)
                                    }
                                }
                            }
                        }
                    }
                    
                    val frequent = allContacts.filter { favoriteNumbers.contains(it.phoneNumber) }.take(3)
                    
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(16.dp),
                        contentPadding = PaddingValues(start = 8.dp, top = 0.dp, end = 8.dp, bottom = 16.dp)
                    ) {
                        items(frequent) { contact ->
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                modifier = Modifier.combinedClickable(
                                    onClick = {
                                        if (mistouchPrevention) {
                                            callToConfirm = Pair(contact.name, contact.phoneNumber)
                                        } else {
                                            CallManager.makeCall(context, contact.phoneNumber)
                                        }
                                    },
                                    onLongClick = {
                                        favoriteNumbers.remove(contact.phoneNumber)
                                        sharedPrefs.edit().putStringSet("KEY_FAVORITES", favoriteNumbers.toSet()).apply()
                                        view.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
                                    }
                                )
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
                        if (frequent.size < 3) {
                            item {
                                Column(
                                    horizontalAlignment = Alignment.CenterHorizontally,
                                    modifier = Modifier.clickable {
                                        showContactPicker = true
                                    }
                                ) {
                                    Box(
                                        contentAlignment = Alignment.Center,
                                        modifier = Modifier.size(56.dp).clip(CircleShape).background(Color.White).border(1.dp, Color(0xFFE2E8F0), CircleShape)
                                    ) {
                                        Text("+", fontSize = 24.sp, color = TextSecondary, fontWeight = FontWeight.Light)
                                    }
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        text = "Add",
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = TextSecondary,
                                        maxLines = 1,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                }
                            }
                        }
                    }
                }
            }

            item {
                Text(
                    "Recents", 
                    fontSize = 28.sp, 
                    fontWeight = FontWeight.Bold, 
                    color = TextPrimary,
                    modifier = Modifier.padding(start = 8.dp, top = 8.dp, end = 0.dp, bottom = 16.dp)
                )
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
                                onViewHistory = { selectedHistoryContact = call.number },
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
            }

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
    }
}

@androidx.compose.material3.ExperimentalMaterial3Api
@Composable
fun CallHistoryItemCard(
    item: HomeCallItem, 
    mistouchPrevention: Boolean,
    onViewHistory: () -> Unit = {},
    onDelete: (HomeCallItem) -> Unit
) {
    val context = LocalContext.current
    val view = LocalView.current
    var expanded by remember { mutableStateOf(false) }
    var callToConfirm by remember { mutableStateOf<String?>(null) }
    var showLongPressMenu by remember { mutableStateOf(false) }
    
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
                        showLongPressMenu = true
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
                        onClick = onViewHistory,
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

    if (showLongPressMenu) {
        ModalBottomSheet(
            onDismissRequest = { showLongPressMenu = false },
            containerColor = PlateBackground
        ) {
            Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                        val clip = android.content.ClipData.newPlainText("Phone Number", item.number)
                        clipboard.setPrimaryClip(clip)
                        android.widget.Toast.makeText(context, "Copied to clipboard", android.widget.Toast.LENGTH_SHORT).show()
                        showLongPressMenu = false
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.ContentCopy, contentDescription = "Copy")
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Copy Phone Number", fontSize = 16.sp)
                }
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        onDelete(item)
                        showLongPressMenu = false
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Delete, contentDescription = "Delete", tint = Color.Red)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Delete Call Log", fontSize = 16.sp, color = Color.Red)
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

@Composable
fun Avatar(name: String?, size: androidx.compose.ui.unit.Dp = 40.dp) {

    val displayName = name ?: "?"
    val color = getAvatarColor(displayName)
    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier.size(size).clip(CircleShape).background(color)
    ) {
        Text(
            text = displayName.take(1).uppercase(),
            fontSize = (size.value * 0.45).sp,
            fontWeight = FontWeight.Medium,
            color = TextPrimary
        )
    }
}
