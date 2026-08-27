package com.titan.zapdial

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.ContactsContract
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

data class Contact(
    val id: String,
    val name: String,
    val phoneNumber: String,
    val photoUri: Uri?,
    val accountName: String? = null
)

object ContactFetcher {
    suspend fun fetchContacts(context: Context): List<Contact> = withContext(Dispatchers.IO) {
        val contactsList = mutableListOf<Contact>()

        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) != PackageManager.PERMISSION_GRANTED) {
            return@withContext emptyList()
        }

        try {
            val contentResolver = context.contentResolver
            val accountMap = mutableMapOf<String, String>()
            
            try {
                val rawCursor = contentResolver.query(
                    ContactsContract.RawContacts.CONTENT_URI,
                    arrayOf(ContactsContract.RawContacts.CONTACT_ID, ContactsContract.RawContacts.ACCOUNT_NAME),
                    null, null, null
                )
                rawCursor?.use {
                    val contactIdIdx = it.getColumnIndex(ContactsContract.RawContacts.CONTACT_ID)
                    val accountNameIdx = it.getColumnIndex(ContactsContract.RawContacts.ACCOUNT_NAME)
                    while (it.moveToNext()) {
                        val cId = if (contactIdIdx != -1) it.getString(contactIdIdx) else null
                        val aName = if (accountNameIdx != -1) it.getString(accountNameIdx) ?: "Device / Local" else "Device / Local"
                        if (cId != null) accountMap[cId] = aName
                    }
                }
            } catch (e: Exception) { e.printStackTrace() }

            val projection = arrayOf(
                ContactsContract.CommonDataKinds.Phone.CONTACT_ID,
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
                ContactsContract.CommonDataKinds.Phone.NUMBER,
                ContactsContract.CommonDataKinds.Phone.PHOTO_URI
            )
            
            try {
                val cursor = contentResolver.query(
                    ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                    projection, null, null,
                    "${ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME} ASC"
                )
                
                cursor?.use {
                    val idIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.CONTACT_ID)
                    val nameIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
                    val numberIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                    val photoIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.PHOTO_URI)
                    
                    while (it.moveToNext()) {
                        val id = if (idIndex != -1) it.getString(idIndex).orEmpty() else ""
                        val name = if (nameIndex != -1) it.getString(nameIndex).orEmpty() else "Unknown"
                        val rawNumber = if (numberIndex != -1) it.getString(numberIndex).orEmpty() else ""
                        val photoUriString = if (photoIndex != -1) it.getString(photoIndex) else null
                        
                        val photoUri = photoUriString?.let { uriStr -> 
                            try { Uri.parse(uriStr) } catch (e: Exception) { null }
                        }
                        val accName = accountMap[id] ?: "Device / Local"
                        
                        if (rawNumber.isNotBlank()) {
                            contactsList.add(
                                Contact(
                                    id = id,
                                    name = name,
                                    phoneNumber = rawNumber.trim(),
                                    photoUri = photoUri,
                                    accountName = accName
                                )
                            )
                        }
                    }
                }
            } catch (e: Exception) { e.printStackTrace() }
        } catch (e: SecurityException) {
            e.printStackTrace()
        }

        contactsList.distinctBy {
            "${it.name}_${it.phoneNumber.replace("[^0-9+]".toRegex(), "")}"
        }
    }
}
