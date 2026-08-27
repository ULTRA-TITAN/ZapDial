package com.titan.zapdial

import android.Manifest
import android.app.role.RoleManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.telecom.Call
import android.telecom.TelecomManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Dialpad
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Contacts
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController

class MainActivity : ComponentActivity() {
    override fun onResume() {
        super.onResume()
        CallSessionManager.isAppInForeground = true
    }

    override fun onPause() {
        super.onPause()
        CallSessionManager.isAppInForeground = false
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O_MR1) {
            setShowWhenLocked(true)
            setTurnScreenOn(true)
        } else {
            @Suppress("DEPRECATION")
            window.addFlags(
                android.view.WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or
                android.view.WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON
            )
        }
        window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContent {
            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = Color(0xFFF7F9FC)
                ) {
                    AppNavigationContainer(intent)
                }
            }
        }
    }
}

@Composable
fun AppNavigationContainer(intent: Intent?) {
    val context = LocalContext.current
    val callState by CallSessionManager.callState.collectAsState()
    val activeCall by CallSessionManager.activeCall.collectAsState()
    
    val rawCallerNumber = activeCall?.details?.handle?.schemeSpecificPart ?: "Unknown Number"
    var resolvedCallerName by remember { mutableStateOf<String?>(null) }
    
    LaunchedEffect(rawCallerNumber) {
        if (rawCallerNumber != "Unknown Number") {
            val name = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                ContactFetcher.lookupContactName(context, rawCallerNumber)
            }
            resolvedCallerName = name
        } else {
            resolvedCallerName = null
        }
    }
    
    val callerNumber = rawCallerNumber
    val originalCallerName = activeCall?.details?.callerDisplayName
    val callerName = resolvedCallerName ?: originalCallerName ?: callerNumber

    if (callState == Call.STATE_RINGING) {
        IncomingCallScreen(
            callerName = callerName,
            callerNumber = callerNumber
        )
    } else if (callState == Call.STATE_ACTIVE || callState == Call.STATE_DIALING || callState == Call.STATE_HOLDING || callState == Call.STATE_CONNECTING) {
        OngoingCallScreen(
            callerName = callerName,
            callerNumber = callerNumber
        )
    } else {
        val startRoute = intent?.getStringExtra("start_route") ?: "home"
        MainHomeScreen(startRoute)
    }
}

@Composable
fun MainHomeScreen(startRoute: String) {
    val context = LocalContext.current
    val roleManager = context.getSystemService(Context.ROLE_SERVICE) as? RoleManager
    val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as? TelecomManager
    
    val defaultDialerLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
        contract = androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult()
    ) { _ -> }

    LaunchedEffect(Unit) {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.Q) {
            if (roleManager?.isRoleHeld(RoleManager.ROLE_DIALER) == false) {
                val intent = roleManager.createRequestRoleIntent(RoleManager.ROLE_DIALER)
                defaultDialerLauncher.launch(intent)
            }
        } else {
            if (telecomManager?.defaultDialerPackage != context.packageName) {
                val intent = android.content.Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER)
                intent.putExtra(TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME, context.packageName)
                defaultDialerLauncher.launch(intent)
            }
        }
    }


    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var hasSeenOnboarding by remember {
        mutableStateOf(sharedPrefs.getBoolean("hasSeenOnboarding", false))
    }

    if (!hasSeenOnboarding) {
        PermissionPrimerScreen(
            onDismiss = {
                sharedPrefs.edit().putBoolean("hasSeenOnboarding", true).apply()
                hasSeenOnboarding = true
            }
        )
        return
    }

    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            val navBackStackEntry by navController.currentBackStackEntryAsState()
            val currentRoute = navBackStackEntry?.destination?.route
            if (currentRoute != "settings") {
                NavigationBar {
                    NavigationBarItem(
                        icon = { Icon(Icons.Filled.Dialpad, contentDescription = "Keypad") },
                        label = { Text("Keypad") },
                        selected = currentRoute == "keypad",
                        onClick = {
                            if (currentRoute != "keypad") {
                                navController.navigate("keypad") {
                                    popUpTo(navController.graph.startDestinationId)
                                    launchSingleTop = true
                                }
                            }
                        }
                    )
                    NavigationBarItem(
                        icon = { Icon(Icons.Filled.Home, contentDescription = "Home") },
                        label = { Text("Home") },
                        selected = currentRoute == "home",
                        onClick = {
                            if (currentRoute != "home") {
                                navController.navigate("home") {
                                    popUpTo(navController.graph.startDestinationId)
                                    launchSingleTop = true
                                }
                            }
                        }
                    )
                    NavigationBarItem(
                        icon = { Icon(Icons.Filled.Contacts, contentDescription = "Contacts") },
                        label = { Text("Contacts") },
                        selected = currentRoute == "contacts",
                        onClick = {
                            if (currentRoute != "contacts") {
                                navController.navigate("contacts") {
                                    popUpTo(navController.graph.startDestinationId)
                                    launchSingleTop = true
                                }
                            }
                        }
                    )
                }
            }
        }
    ) { paddingValues ->
        Box(modifier = Modifier.padding(paddingValues)) {
            NavHost(navController, startDestination = startRoute) {
                composable("keypad") { DialPadScreen() }
                composable("home") { HomeScreen(onNavigateToSettings = { navController.navigate("settings") }) }
                composable("contacts") { ContactsScreen() }
                composable("settings") { SettingsScreen(onBack = { navController.popBackStack() }) }
            }
        }
    }
}
