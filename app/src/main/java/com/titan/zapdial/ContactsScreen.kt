package com.titan.zapdial

import android.Manifest
import android.content.Context
import android.telecom.PhoneAccountHandle
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.drag
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.TransformOrigin
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.layout.positionInParent
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.Dispatchers
import kotlin.math.absoluteValue

// Exact Design System Colors
private val PageBackground = Color(0xFFFFFFFF)
private val PlateBackground = Color(0xFFFFFFFF)
private val TextPrimary = Color(0xFF0F172A)
private val TextSecondary = Color(0xFF64748B)
private val RailInactive = Color(0xFFD8D8D6)
private val BubbleColor = Color(0xFF2A2A2E)
private val BubbleTextColor = Color(0xFFFDFCFA)
private val AvatarTextColor = Color(0xFF44444C)

private val AvatarPalette = listOf(
    Color(0xFFAFC4E0), Color(0xFFAECBB8), Color(0xFFE0B3AE), Color(0xFFC9BEE0),
    Color(0xFFE0B8CB), Color(0xFFE0CBA6), Color(0xFFA9CFC9), Color(0xFFC7C7CE)
)

private val LETTERS = ('A'..'Z').toList()

private fun avatarColorFor(name: String): Color {
    if (name.isBlank()) return AvatarPalette.last()
    val hash = name.hashCode().absoluteValue
    return AvatarPalette[hash % AvatarPalette.size]
}

private sealed class DirectoryRow {
    data class Header(val letter: Char) : DirectoryRow()
    data class Item(val contact: Contact) : DirectoryRow()
}

@Composable
@OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)
fun ContactsScreen() {
    val context = LocalContext.current
    var showSimSelectionFor by remember { mutableStateOf<String?>(null) }
    var availableSimsForCall by remember { mutableStateOf<List<android.telecom.PhoneAccountHandle>>(emptyList()) }
    
    if (showSimSelectionFor != null) {
        SimSelectionDialog(
            context = context,
            availableSims = availableSimsForCall,
            onSimSelected = { handle ->
                CallManager.makeCall(context, showSimSelectionFor!!, handle)
                showSimSelectionFor = null
            },
            onDismiss = { showSimSelectionFor = null }
        )
    }

    var allContacts by remember { mutableStateOf<List<Contact>>(emptyList()) }
    
    LaunchedEffect(Unit) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) == PackageManager.PERMISSION_GRANTED) {
            allContacts = ContactFetcher.fetchContacts(context)
        }
    }

    var selectedFilter by remember { mutableStateOf("All") }
    var directory by remember { mutableStateOf<Map<Char, List<Contact>>>(emptyMap()) }
    

    LaunchedEffect(allContacts, selectedFilter) {
        withContext(Dispatchers.Default) {
            val map = mutableMapOf<Char, MutableList<Contact>>()
            val filtered = allContacts.filter { 
                when (selectedFilter) {
                    "SIM 1" -> it.accountName?.contains("SIM", true) == true
                    "Google" -> it.accountName?.contains("Google", true) == true || it.accountName?.contains("@", true) == true
                    else -> true
                }
            }
            filtered.forEach { contact ->
                val firstChar = contact.name.firstOrNull()?.uppercaseChar() ?: '#'
                val key = if (firstChar in LETTERS) firstChar else '#'
                map.getOrPut(key) { mutableListOf() }.add(contact)
            }
            directory = map.mapValues { it.value.sortedBy { c -> c.name } }
        }
    }

    val rows = remember(directory) {
        val list = mutableListOf<DirectoryRow>()
        for (letter in LETTERS) {
            val contacts = directory[letter]
            if (!contacts.isNullOrEmpty()) {
                list.add(DirectoryRow.Header(letter))
                contacts.forEach { list.add(DirectoryRow.Item(it)) }
            }
        }
        val others = directory['#']
        if (!others.isNullOrEmpty()) {
            list.add(DirectoryRow.Header('#'))
            others.forEach { list.add(DirectoryRow.Item(it)) }
        }
        list
    }

    val letterRowIndex = remember(rows) {
        val map = mutableMapOf<Char, Int>()
        rows.forEachIndexed { index, row ->
            if (row is DirectoryRow.Header && !map.containsKey(row.letter)) {
                map[row.letter] = index
            }
        }
        map
    }

    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()
    val haptic = LocalHapticFeedback.current

    var railTopPx by remember { mutableStateOf(0f) }
    var railHeightPx by remember { mutableStateOf(1f) }
    var currentLetter by remember { mutableIntStateOf(-1) }
    var lastSnappedLetter by remember { mutableStateOf<Char?>(null) }
    var showContactOptionsFor by remember { mutableStateOf<Contact?>(null) }

    
    
    
    

    val extendedStemWidth = 30f
    val bubbleSizeDp = 64.dp

    suspend fun snapToLetter(letter: Char) {
        val targetIndex = letterRowIndex[letter] ?: run {
            var idx = LETTERS.indexOf(letter)
            var found: Int? = null
            while (idx >= 0 && found == null) {
                found = letterRowIndex[LETTERS[idx]]
                idx--
            }
            found
        }
        if (targetIndex != null) {
            listState.scrollToItem(targetIndex)
        }
    }

    var isDragging by remember { mutableStateOf(false) }
    var bubbleYRaw by remember { mutableStateOf(0f) }

    val bubbleScale by androidx.compose.animation.core.animateFloatAsState(if (isDragging) 1f else 0.2f, androidx.compose.animation.core.tween(if(isDragging) 180 else 300, easing = if(isDragging) androidx.compose.animation.core.FastOutSlowInEasing else androidx.compose.animation.core.CubicBezierEasing(0.6f, -0.1f, 0.75f, 0.15f)))
    val bubbleOpacity by androidx.compose.animation.core.animateFloatAsState(if (isDragging) 1f else 0f, androidx.compose.animation.core.tween(if(isDragging) 120 else 280))
    val stemWidthState by androidx.compose.animation.core.animateFloatAsState(if (isDragging) extendedStemWidth else 0f, androidx.compose.animation.core.tween(if(isDragging) 140 else 260, easing = if(isDragging) androidx.compose.animation.core.FastOutSlowInEasing else androidx.compose.animation.core.CubicBezierEasing(0.6f, -0.1f, 0.75f, 0.15f)))

    fun onDragAt(yInContainer: Float) {
        isDragging = true
        bubbleYRaw = yInContainer
        val relY = (yInContainer - railTopPx).coerceIn(0f, railHeightPx)
        val ratio = (relY / railHeightPx).coerceIn(0f, 1f)
        val idx = (ratio * (LETTERS.size - 1)).toInt().coerceIn(0, LETTERS.size - 1)
        currentLetter = idx
        val letter = LETTERS[idx]
        if (letter != lastSnappedLetter) {
            lastSnappedLetter = letter
            haptic.performHapticFeedback(androidx.compose.ui.hapticfeedback.HapticFeedbackType.TextHandleMove)
            scope.launch { snapToLetter(letter) }
        }
    }

    fun onDragEnd() {
        isDragging = false
        currentLetter = -1
        lastSnappedLetter = null
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(PageBackground)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            Text(
                text = "Contacts",
                fontSize = 34.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary,
                modifier = Modifier.padding(start = 24.dp, top = 32.dp, bottom = 16.dp)
            )
            
            // Filter Row
            
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp)
                    .padding(bottom = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf("All", "SIM 1", "Google").forEach { filter ->
                    val isSelected = selectedFilter == filter
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(16.dp))
                            .background(if (isSelected) Color(0xFFE5E7EB) else Color.Transparent)
                            .clickable { selectedFilter = filter }
                            .padding(horizontal = 16.dp, vertical = 8.dp)
                    ) {
                        Text(
                            text = filter,
                            fontSize = 14.sp,
                            fontWeight = if (isSelected) FontWeight.Medium else FontWeight.Normal,
                            color = if (isSelected) TextPrimary else TextSecondary
                        )
                    }
                }
            }

            Box(modifier = Modifier.fillMaxSize()) {
                LazyColumn(
                    state = listState,
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(end = 26.dp),
                    contentPadding = PaddingValues(start = 18.dp, end = 18.dp, bottom = 18.dp)
                ) {
                    items(rows, key = { row -> if (row is DirectoryRow.Header) "H_${row.letter}" else "I_${(row as DirectoryRow.Item).contact.id}" }) { row ->
                        when (row) {
                            is DirectoryRow.Header -> {
                                Text(
                                    text = row.letter.toString(),
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Normal,
                                    color = TextSecondary,
                                    modifier = Modifier.padding(start = 6.dp, top = 14.dp, bottom = 6.dp)
                                )
                            }
                            is DirectoryRow.Item -> {
                                ContactPlate(row.contact, onClick = { showContactOptionsFor = row.contact })
                            }
                        }
                    }
                }

                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier
                        .align(Alignment.CenterEnd)
                        .fillMaxHeight()
                        .padding(top = 0.dp, bottom = 18.dp, end = 2.dp)
                        .width(20.dp)
                        .onGloballyPositionedRailBounds { top, height ->
                            railTopPx = top
                            railHeightPx = height
                        }
                        .pointerInput(Unit) {
                            awaitEachGesture {
                                val down = awaitFirstDown()
                                onDragAt(down.position.y + railTopPx)
                                drag(down.id) { change ->
                                    onDragAt(change.position.y + railTopPx)
                                    change.consume()
                                }
                                onDragEnd()
                            }
                        }
                ) {
                    LETTERS.forEachIndexed { index, letter ->
                        val isActive = index == currentLetter
                        val hasContacts = directory.containsKey(letter) && directory[letter]!!.isNotEmpty()
                        Text(
                            text = letter.toString(),
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Normal,
                            color = if (isActive) TextPrimary else if (hasContacts) TextSecondary else RailInactive,
                            modifier = Modifier.graphicsLayer {
                                val scale = if (isActive) 1.7f else 1f
                                scaleX = scale
                                scaleY = scale
                                transformOrigin = TransformOrigin(1f, 0.5f)
                            }
                        )
                    }
                }

                Box(
                    modifier = Modifier
                        .offset {
                            IntOffset(
                                x = 0,
                                y = (bubbleYRaw - 4.dp.toPx()).toInt()
                            )
                        }
                        .align(Alignment.TopEnd)
                        .padding(end = 10.dp)
                        .width(with(LocalDensity.current) { stemWidthState.toDp() })
                        .height(8.dp)
                        .graphicsLayer { alpha = if (bubbleOpacity > 0.05f) 1f else 0f }
                        .background(BubbleColor, RoundedCornerShape(4.dp))
                )

                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .offset {
                            IntOffset(
                                x = 0,
                                y = (bubbleYRaw - (bubbleSizeDp / 2).toPx()).toInt()
                            )
                        }
                        .align(Alignment.TopEnd)
                        .padding(end = 34.dp)
                        .size(bubbleSizeDp)
                        .graphicsLayer {
                            scaleX = bubbleScale
                            scaleY = bubbleScale
                            alpha = bubbleOpacity
                        }
                        .clip(CircleShape)
                        .background(BubbleColor)
                ) {
                    if (currentLetter in LETTERS.indices) {
                        Text(
                            text = LETTERS[currentLetter].toString(),
                            fontSize = 26.sp,
                            fontWeight = FontWeight.Light,
                            color = BubbleTextColor
                        )
                    }
                }
            }
        }
    if (showContactOptionsFor != null) {
        androidx.compose.material3.ModalBottomSheet(onDismissRequest = { showContactOptionsFor = null }, containerColor = PlateBackground) {
            Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
                Text(text = showContactOptionsFor!!.name, fontSize = 20.sp, fontWeight = FontWeight.SemiBold, color = TextPrimary)
                Spacer(modifier = Modifier.height(24.dp))
                val context = LocalContext.current
                val contactId = showContactOptionsFor!!.id
                val number = showContactOptionsFor!!.phoneNumber
                
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        CallManager.initiateCallWithSimCheck(context, number) { sims ->
                            availableSimsForCall = sims
                            showSimSelectionFor = number
                        }
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Call, contentDescription = "Dial")
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Dial Contact", fontSize = 16.sp, color = TextPrimary)
                }
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        val intent = android.content.Intent(android.content.Intent.ACTION_EDIT).apply {
                            try {
                                data = android.content.ContentUris.withAppendedId(android.provider.ContactsContract.Contacts.CONTENT_URI, contactId.toLong())
                            } catch (e: Exception) {}
                        }
                        try { context.startActivity(intent) } catch (e: Exception) {}
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Edit, contentDescription = "Edit")
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Edit Contact", fontSize = 16.sp, color = TextPrimary)
                }
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        try {
                            val uri = android.content.ContentUris.withAppendedId(android.provider.ContactsContract.Contacts.CONTENT_URI, contactId.toLong())
                            context.contentResolver.delete(uri, null, null)
                            scope.launch {
                                allContacts = ContactFetcher.fetchContacts(context)
                            }
                        } catch (e: Exception) {}
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Delete, contentDescription = "Delete", tint = Color.Red)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Delete Contact", fontSize = 16.sp, color = Color.Red)
                }
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        scope.launch(Dispatchers.IO) {
                            val prefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
                            val blocked = prefs.getStringSet("KEY_BLOCKED_NUMBERS", emptySet())?.toMutableSet() ?: mutableSetOf()
                            blocked.add(number)
                            prefs.edit().putStringSet("KEY_BLOCKED_NUMBERS", blocked).commit()
                        }
                        android.widget.Toast.makeText(context, "Contact Blocked", android.widget.Toast.LENGTH_SHORT).show()
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Delete, contentDescription = "Block", tint = Color.Red)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Block Contact", fontSize = 16.sp, color = Color.Red)
                }
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        val intent = android.content.Intent(android.content.Intent.ACTION_VIEW).apply {
                            type = android.provider.CallLog.Calls.CONTENT_TYPE
                            putExtra(android.provider.CallLog.Calls.EXTRA_CALL_TYPE_FILTER, android.provider.CallLog.Calls.INCOMING_TYPE)
                        }
                        try { context.startActivity(intent) } catch (e: Exception) { android.widget.Toast.makeText(context, "Action unavailable", android.widget.Toast.LENGTH_SHORT).show() }
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Edit, contentDescription = "History")
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("View History", fontSize = 16.sp, color = TextPrimary)
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }

    }
}

@Composable
private fun ContactPlate(contact: Contact, onClick: () -> Unit) {
    val context = LocalContext.current
    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var callToConfirm by remember { mutableStateOf<String?>(null) }
    var showSimSelectionFor by remember { mutableStateOf<String?>(null) }
    var availableSimsForCall by remember { mutableStateOf<List<android.telecom.PhoneAccountHandle>>(emptyList()) }
    
    if (showSimSelectionFor != null) {
        SimSelectionDialog(
            context = context,
            availableSims = availableSimsForCall,
            onSimSelected = { handle ->
                CallManager.makeCall(context, showSimSelectionFor!!, handle)
                showSimSelectionFor = null
            },
            onDismiss = { showSimSelectionFor = null }
        )
    }
    
    val callPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            val mistouchPrevention = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
            if (mistouchPrevention) callToConfirm = contact.phoneNumber else CallManager.initiateCallWithSimCheck(context, contact.phoneNumber) { sims ->
                availableSimsForCall = sims
                showSimSelectionFor = contact.phoneNumber
            }
        }
    }
    
    callToConfirm?.let { num ->
        CallConfirmationDialog(
            name = contact.name,
            number = num,
            onConfirm = { CallManager.initiateCallWithSimCheck(context, num) { sims ->
                availableSimsForCall = sims
                showSimSelectionFor = num
            } },
            onDismiss = { callToConfirm = null }
        )
    }

    val color = remember(contact.name) { avatarColorFor(contact.name) }
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(bottom = 7.dp)
            .clip(RoundedCornerShape(16.dp))
            .background(PlateBackground)
            .clickable { onClick() }
            .padding(horizontal = 18.dp, vertical = 12.dp)
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier
                .size(38.dp)
                .clip(CircleShape)
                .background(color)
        ) {
            Text(
                text = contact.name.take(1).uppercase(),
                fontSize = 15.sp,
                fontWeight = FontWeight.Light,
                color = AvatarTextColor
            )
        }
        Text(
            text = contact.name,
            fontSize = 16.sp,
            fontWeight = FontWeight.Normal,
            color = TextPrimary,
            modifier = Modifier
                .align(Alignment.CenterStart)
                .padding(start = 52.dp)
        )
    }
}

@Composable
private fun Modifier.onGloballyPositionedRailBounds(
    onBounds: (top: Float, height: Float) -> Unit
): Modifier = this.then(
    Modifier.then(
        onGloballyPositioned { coordinates ->
            onBounds(coordinates.positionInParent().y, coordinates.size.height.toFloat())
        }
    )
)