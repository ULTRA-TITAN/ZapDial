package com.titan.zapdial

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.view.HapticFeedbackConstants
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Backspace
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.PersonAdd
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.ui.input.pointer.pointerInput
import kotlinx.coroutines.delay
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import kotlinx.coroutines.launch

import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat

fun mapNameToDigits(name: String): String {
    val map = mapOf(
        'A' to '2', 'B' to '2', 'C' to '2',
        'D' to '3', 'E' to '3', 'F' to '3',
        'G' to '4', 'H' to '4', 'I' to '4',
        'J' to '5', 'K' to '5', 'L' to '5',
        'M' to '6', 'N' to '6', 'O' to '6',
        'P' to '7', 'Q' to '7', 'R' to '7', 'S' to '7',
        'T' to '8', 'U' to '8', 'V' to '8',
        'W' to '9', 'X' to '9', 'Y' to '9', 'Z' to '9'
    )
    return name.uppercase().mapNotNull { map[it] }.joinToString("")
}

@Composable
fun DialPadScreen() {
    var number by remember { mutableStateOf("") }
    val coroutineScope = rememberCoroutineScope()
    var allContacts by remember { mutableStateOf<List<Contact>>(emptyList()) }
    val context = LocalContext.current
    val view = LocalView.current
    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    
    LaunchedEffect(Unit) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) == PackageManager.PERMISSION_GRANTED) {
            val fetched = ContactFetcher.fetchContacts(context)
            allContacts = fetched
        }
    }
    
    val matchedContacts by remember(number, allContacts) {
        derivedStateOf {
            if (number.isEmpty()) emptyList()
            else allContacts.filter { 
                it.phoneNumber.replace("[^0-9+]".toRegex(), "").contains(number) || 
                mapNameToDigits(it.name).contains(number) 
            }.take(5)
        }
    }
    val showAddContact = number.length >= 3 && !allContacts.any { it.phoneNumber.replace("[^0-9+]".toRegex(), "") == number }
    var showAddDialog by remember { mutableStateOf(false) }
    
    if (showAddDialog) {
        AddContactDialog(
            initialNumber = number,
            onDismiss = { showAddDialog = false },
            onContactAdded = {
                coroutineScope.launch {
                    if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) == PackageManager.PERMISSION_GRANTED) {
                        allContacts = ContactFetcher.fetchContacts(context)
                    }
                }
            }
        )
    }

    
    var callToConfirm by remember { mutableStateOf<String?>(null) }
    
    fun attemptCall(num: String) {
        val mistouchPrevention = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
        if (mistouchPrevention) {
            callToConfirm = num
        } else {
            CallManager.makeCall(context, num)
            number = ""
        }
    }

    val callPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted && number.isNotEmpty()) {
            attemptCall(number)
        }
    }
    
    callToConfirm?.let { num ->
        CallConfirmationDialog(
            name = null,
            number = num,
            onConfirm = {
                CallManager.makeCall(context, num)
                number = ""
                callToConfirm = null
            },
            onDismiss = { callToConfirm = null }
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFFFF8E8)) // Soft warm cream
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Bottom
    ) {
        // Display Area
        Column(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            verticalArrangement = Arrangement.Bottom,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            if (matchedContacts.isNotEmpty() || showAddContact) {
                androidx.compose.foundation.lazy.LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    contentPadding = PaddingValues(horizontal = 16.dp),
                    modifier = Modifier.padding(bottom = 16.dp).fillMaxWidth().weight(1f, fill = false)
                ) {
                    items(matchedContacts.size) { index ->
                        val contact = matchedContacts[index]
                        Surface(
                            shape = RoundedCornerShape(16.dp),
                            color = Color.White,
                            shadowElevation = 0.dp,
                            modifier = Modifier.fillMaxWidth().clickable { attemptCall(contact.phoneNumber) }
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Avatar(name = contact.name, size = 40.dp)
                                Spacer(modifier = Modifier.width(16.dp))
                                Column {
                                    Text(contact.name, fontSize = 16.sp, fontWeight = FontWeight.Normal, color = Color(0xFF2A2A2E))
                                    Text(contact.phoneNumber, fontSize = 14.sp, fontWeight = FontWeight.Light, color = Color(0xFF9A9AA2))
                                }
                            }
                        }
                    }
                    if (showAddContact) {
                        item {
                            Surface(
                                shape = RoundedCornerShape(16.dp),
                                color = Color(0xFFF3F4F6),
                                modifier = Modifier.fillMaxWidth().clickable { showAddDialog = true }
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 16.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.Center
                                ) {
                                    Icon(Icons.Default.PersonAdd, contentDescription = null, tint = Color(0xFF0F172A), modifier = Modifier.size(24.dp))
                                    Spacer(modifier = Modifier.width(12.dp))
                                    Text("Add to Contacts", fontSize = 16.sp, fontWeight = FontWeight.Medium, color = Color(0xFF0F172A))
                                }
                            }
                        }
                    }
                }
            }
            Text(
                text = number,
                fontSize = 42.sp,
                fontWeight = FontWeight.SemiBold,
                color = Color(0xFF0F172A),
                maxLines = 1,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(bottom = 24.dp)
            )
        }

        // Keypad Grid
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            val rows = listOf(
                listOf(DialKey("1", ""), DialKey("2", "ABC"), DialKey("3", "DEF")),
                listOf(DialKey("4", "GHI"), DialKey("5", "JKL"), DialKey("6", "MNO")),
                listOf(DialKey("7", "PQRS"), DialKey("8", "TUV"), DialKey("9", "WXYZ")),
                listOf(DialKey("*", ""), DialKey("0", "+"), DialKey("#", ""))
            )

            for (row in rows) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    for (key in row) {
                        DialButton(
                            digit = key.digit,
                            letters = key.letters,
                            onClick = {
                                view.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP)
                                number += key.digit
                            },
                            onLongClick = {
                                if (key.digit == "0") {
                                    view.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
                                    number += "+"
                                }
                            }
                        )
                    }
                }
            }

            // Bottom Actions (Call & Backspace)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 16.dp, bottom = 32.dp),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Spacer(modifier = Modifier.size(64.dp)) // Spacer for alignment

                // Call Button
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .size(72.dp)
                        .clip(CircleShape)
                        .background(Color(0xFF16A34A)) // Vibrant Green
                        .clickable {
                            view.performHapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY)
                            if (number.isNotEmpty()) {
                                if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                                    attemptCall(number)
                                } else {
                                    callPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
                                }
                            }
                        }
                ) {
                    Icon(
                        imageVector = Icons.Default.Call,
                        contentDescription = "Call",
                        tint = Color.White,
                        modifier = Modifier.size(36.dp)
                    )
                }

                // Backspace Button
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .size(64.dp)
                        .clip(CircleShape)
                        .pointerInput(Unit) {
                            awaitEachGesture {
                                val down = awaitFirstDown()
                                if (number.isNotEmpty()) {
                                    view.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP)
                                    number = number.dropLast(1)
                                }
                                val job = coroutineScope.launch {
                                    delay(500)
                                    while (number.isNotEmpty()) {
                                        view.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP)
                                        number = number.dropLast(1)
                                        delay(100)
                                    }
                                }
                                do { val event = awaitPointerEvent() } while (event.changes.any { it.pressed })
                                job.cancel()
                            }
                        }
                ) {
                    Icon(
                        imageVector = Icons.Default.Backspace,
                        contentDescription = "Backspace",
                        tint = Color(0xFF64748B),
                        modifier = Modifier.size(28.dp)
                    )
                }
            }
        }
    }
}

data class DialKey(val digit: String, val letters: String)

@OptIn(androidx.compose.foundation.ExperimentalFoundationApi::class)
@Composable
fun DialButton(digit: String, letters: String, onClick: () -> Unit, onLongClick: () -> Unit = {}) {
    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier
            .size(72.dp) // Reduced from 80dp
            .shadow(2.dp, CircleShape)
            .clip(CircleShape)
            .background(Color(0xFFFFFFFF)) // Soft White
            .combinedClickable(
                onClick = onClick,
                onLongClick = onLongClick
            )
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = digit,
                fontSize = 28.sp, // A bit smaller than 32
                fontWeight = FontWeight.Medium,
                color = Color(0xFF0F172A)
            )
            if (letters.isNotEmpty()) {
                Text(
                    text = letters,
                    fontSize = 10.sp,
                    color = Color(0xFF64748B),
                    fontWeight = FontWeight.Normal
                )
            }
        }
    }
}
