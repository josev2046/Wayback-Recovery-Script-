In the event that both primary and backup servers fail, the Internet Archive’s Wayback Machine may contain the final accessible version of a digital collection. This script provides a systematic framework for interpreting that archived content not simply as a static website, but as a compromised database. Its primary objective is to reconstruct the full structured metadata hierarchy and to retrieve all related media files from the preserved HTML snapshots.

Fig.1 shows the logical steps the script follows to recover the collection:

<img width="809" height="902" alt="image" src="https://github.com/user-attachments/assets/99f349c9-1c6b-412b-9bcb-fe2ce76ce212" />

The script executes a two-pronged strategy to ensure maximum data retrieval and media accessibility:

1.  **Granular Metadata Extraction (Dual Strategy):** This method guarantees capture of every descriptive field:

    * **Precision Targeting:** Focuses on specific HTML classes (`div.name`/`div.value`) common to professional catalogue platforms (e.g., AtoM).
    
    * **Robust Fallback:** Implements a search for standard HTML definition lists (`<dl>`, `<dt>`, `<dd>`) for any leftover or custom fields.
    
2.  **URL Negotiation and Media Retrieval:** This addresses the technical hurdle of downloading files hosted externally:

    * **Wayback Prefix Cleansing:** The script automatically strips the Wayback Machine's timestamp prefix from media links. This is the crucial step that prevents common **HTTP 403 Forbidden** errors, allowing the external utility, **`yt-dlp`**, to access the original media resource successfully.

The script performs two main tasks:

* Metadata Extraction: It uses a dual method to ensure it captures every descriptive field on an item's page:

** Direct Search: Targets specific HTML classes (div.name/div.value) common to professional catalogue software.

** Fallback: Checks standard HTML definition lists (<dl>, <dt>, <dd>) for any leftover or custom fields.

* Media Retrieval: It addresses the critical issue of downloading files from the Wayback Machine:

** URL Cleaning: It automatically strips the Wayback Machine's timestamp prefix from media links. This prevents the common HTTP 403 Forbidden error and allows the external tool, yt-dlp, to access the original media file.

# Wayback-Recovery-Script-
Your primary and back-up servers failed? The Wayback Machine may still hold a snapshot of the archive? This script systematically treats archived HTML as a compromised database to reconstruct the full metadata tree and retrieve media files.

```bash
curl -X POST "<YOUR_NUCLEUS_BASE_URL>/api/entries.php" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "awardId=<YOUR_AWARD_ID>&entryId=<YOUR_ENTRY_ID>&expires=<GENERATED_EXPIRES_TIMESTAMP>&keyId=<YOUR_API_KEY_ID>&signature=<GENERATED_SIGNATURE>"
```

`HTML`


