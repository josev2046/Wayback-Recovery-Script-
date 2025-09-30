# Wayback-Recovery-Script-
Your primary and back-up servers failed? The Wayback Machine may still hold a snapshot of the archive? This script systematically treats archived HTML as a compromised database to reconstruct the full metadata tree and retrieve media files.

```bash
curl -X POST "<YOUR_NUCLEUS_BASE_URL>/api/entries.php" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "awardId=<YOUR_AWARD_ID>&entryId=<YOUR_ENTRY_ID>&expires=<GENERATED_EXPIRES_TIMESTAMP>&keyId=<YOUR_API_KEY_ID>&signature=<GENERATED_SIGNATURE>"
```

`HTML`


