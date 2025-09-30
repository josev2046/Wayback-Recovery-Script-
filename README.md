In the event that both primary and backup servers fail, the Internet Archive’s Wayback Machine may contain the final accessible version of a digital collection. This script provides a systematic framework for interpreting that archived content not simply as a static website, but as a compromised database. Its primary objective is to reconstruct the full structured metadata hierarchy and to retrieve all related media files from the preserved HTML snapshots.

Fig.1 shows the logical steps the script follows to recover the collection:

<img width="809" height="902" alt="image" src="https://github.com/user-attachments/assets/99f349c9-1c6b-412b-9bcb-fe2ce76ce212" />



# Wayback-Recovery-Script-
Your primary and back-up servers failed? The Wayback Machine may still hold a snapshot of the archive? This script systematically treats archived HTML as a compromised database to reconstruct the full metadata tree and retrieve media files.

```bash
curl -X POST "<YOUR_NUCLEUS_BASE_URL>/api/entries.php" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "awardId=<YOUR_AWARD_ID>&entryId=<YOUR_ENTRY_ID>&expires=<GENERATED_EXPIRES_TIMESTAMP>&keyId=<YOUR_API_KEY_ID>&signature=<GENERATED_SIGNATURE>"
```

`HTML`


