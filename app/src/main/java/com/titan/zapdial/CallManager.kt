package com.titan.zapdial

import android.Manifest
import android.app.role.RoleManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.telecom.TelecomManager
import android.telecom.PhoneAccountHandle
import android.telephony.SubscriptionManager
import android.widget.Toast
import androidx.core.content.ContextCompat

object CallManager {
    fun isDefaultDialer(context: Context): Boolean {
        val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
        return telecomManager.defaultDialerPackage == context.packageName
    }

    fun requestDefaultDialer(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val roleManager = context.getSystemService(Context.ROLE_SERVICE) as RoleManager
            val intent = roleManager.createRequestRoleIntent(RoleManager.ROLE_DIALER)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            try { context.startActivity(intent) } catch (e: Exception) { android.widget.Toast.makeText(context, "Action unavailable", android.widget.Toast.LENGTH_SHORT).show() }
        } else {
            val intent = Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER)
            intent.putExtra(TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME, context.packageName)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            try { context.startActivity(intent) } catch (e: Exception) { android.widget.Toast.makeText(context, "Action unavailable", android.widget.Toast.LENGTH_SHORT).show() }
        }
    }

    /**
     * Dials a given phone number directly.
     * Sanitizes input to avoid invalid dial string crashes.
     */
    fun getAvailableSims(context: Context): List<PhoneAccountHandle> {
        val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED) {
            val activeSubs = android.telephony.SubscriptionManager.from(context).activeSubscriptionInfoList
            return telecomManager.callCapablePhoneAccounts
        }
        return emptyList()
    }

    fun getSimLabel(context: Context, handle: PhoneAccountHandle): String {
        val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
        return telecomManager.getPhoneAccount(handle)?.label?.toString() ?: "Unknown SIM"
    }


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

    fun makeCall(context: Context, rawPhoneNumber: String, accountHandle: PhoneAccountHandle? = null) {
        if (!isDefaultDialer(context)) {
            requestDefaultDialer(context)
            return
        }

        val cleanNumber = rawPhoneNumber.replace("[^0-9+]".toRegex(), "")
        if (cleanNumber.isBlank()) {
            Toast.makeText(context, "Invalid phone number", Toast.LENGTH_SHORT).show()
            return
        }

        val hasCallPermission = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.CALL_PHONE
        ) == PackageManager.PERMISSION_GRANTED

        val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager

        if (hasCallPermission) {
            try {
                telecomManager.placeCall(
                    Uri.parse("tel:$cleanNumber"),
                    Bundle().apply { 
                        putBoolean(TelecomManager.EXTRA_START_CALL_WITH_SPEAKERPHONE, false)
                        if (accountHandle != null) {
                            putParcelable(TelecomManager.EXTRA_PHONE_ACCOUNT_HANDLE, accountHandle)
                        }
                    }
                )
            } catch (e: SecurityException) {
                Toast.makeText(context, "Call failed: Permission denied", Toast.LENGTH_SHORT).show()
            }
        } else {
            Toast.makeText(context, "Permission denied to make call", Toast.LENGTH_SHORT).show()
        }
    }
}
