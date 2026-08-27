package com.titan.zapdial

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.provider.CallLog
import android.telephony.SubscriptionManager
import android.util.Log
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

object CallLogFetcher {
    suspend fun fetchCallHistory(context: Context, defaultLocation: String, savedContacts: List<Contact> = emptyList()): List<HomeCallItem> {
        return withContext(Dispatchers.IO) {
            val history = mutableListOf<HomeCallItem>()
            
            if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CALL_LOG) != PackageManager.PERMISSION_GRANTED) {
                return@withContext history
            }
            
            val subscriptionManager = context.getSystemService(Context.TELEPHONY_SUBSCRIPTION_SERVICE) as? SubscriptionManager
            val simMap = mutableMapOf<String, String>()
            if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED) {
                try {
                    val activeSubs = subscriptionManager?.activeSubscriptionInfoList
                    activeSubs?.forEach { subInfo ->
                        simMap[subInfo.iccId] = subInfo.displayName?.toString() ?: "SIM ${subInfo.simSlotIndex + 1}"
                    }
                } catch (e: Exception) {
                    Log.e("CallLogFetcher", "Error fetching SIMs", e)
                }
            }
            
            try {
                val projection = arrayOf(
                    CallLog.Calls._ID,
                    CallLog.Calls.NUMBER,
                    CallLog.Calls.CACHED_NAME,
                    CallLog.Calls.TYPE,
                    CallLog.Calls.DATE,
                    CallLog.Calls.DURATION,
                    CallLog.Calls.GEOCODED_LOCATION,
                    CallLog.Calls.PHONE_ACCOUNT_ID
                )
                
                val cursor = context.contentResolver.query(
                    CallLog.Calls.CONTENT_URI,
                    projection,
                    null,
                    null,
                    "${CallLog.Calls.DATE} DESC"
                )
                
                cursor?.use {
                    val idIndex = it.getColumnIndex(CallLog.Calls._ID)
                    val numberIndex = it.getColumnIndex(CallLog.Calls.NUMBER)
                    val nameIndex = it.getColumnIndex(CallLog.Calls.CACHED_NAME)
                    val typeIndex = it.getColumnIndex(CallLog.Calls.TYPE)
                    val dateIndex = it.getColumnIndex(CallLog.Calls.DATE)
                    val durationIndex = it.getColumnIndex(CallLog.Calls.DURATION)
                    val geoIndex = it.getColumnIndex(CallLog.Calls.GEOCODED_LOCATION)
                    val simIndex = it.getColumnIndex(CallLog.Calls.PHONE_ACCOUNT_ID)
                    
                    var count = 0
                    while (it.moveToNext() && count < 200) {
                        val idStr = if (idIndex != -1) it.getString(idIndex) ?: "" else ""
                        val numberStr = if (numberIndex != -1) it.getString(numberIndex) ?: "Unknown" else "Unknown"
                        var nameStr = if (nameIndex != -1) it.getString(nameIndex) else null
                        
                        val matchedContact = savedContacts.find { contact -> 
                            contact.phoneNumber.replace("[^0-9+]".toRegex(), "").contains(numberStr.replace("[^0-9+]".toRegex(), "")) ||
                            numberStr.replace("[^0-9+]".toRegex(), "").contains(contact.phoneNumber.replace("[^0-9+]".toRegex(), ""))
                        }
                        if (matchedContact != null) {
                            nameStr = matchedContact.name
                        }
                        
                        val typeInt = if (typeIndex != -1) it.getInt(typeIndex) else CallLog.Calls.INCOMING_TYPE
                        val dateLong = if (dateIndex != -1) it.getLong(dateIndex) else 0L
                        val durationLong = if (durationIndex != -1) it.getLong(durationIndex) else 0L
                        val geoStr = if (geoIndex != -1 && !it.getString(geoIndex).isNullOrEmpty()) it.getString(geoIndex) else defaultLocation
                        val simId = if (simIndex != -1) it.getString(simIndex) else null
                        val simName = simMap.values.elementAtOrNull(0) ?: "SIM 1"
                        
                        history.add(
                            HomeCallItem(
                                id = idStr,
                                number = numberStr,
                                name = nameStr,
                                type = typeInt,
                                date = dateLong,
                                duration = durationLong,
                                location = geoStr,
                                simName = simName
                            )
                        )
                        count++
                    }
                }
            } catch (e: Exception) {
                Log.e("CallLogFetcher", "Error fetching call logs", e)
            }
            
            history
        }
    }
}
