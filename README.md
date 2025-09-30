## Recovery Workflow Logic

In the event that both primary and backup servers fail, the Internet Archive’s Wayback Machine may contain the final accessible version of a digital collection. This script provides a systematic framework for interpreting that archived content not simply as a static website, but as a **compromised database**. Its primary objective is to **reconstruct the full structured metadata hierarchy** and to **retrieve all related media files** from the preserved HTML snapshots.

Fig. 1 shows the logical steps the script follows to recover the collection:

![Logical steps for archive recovery](https://github.com/user-attachments/assets/99f349c9-1c6b-412b-9bcb-fe2ce76ce212)

<p align="center">Fig. 1: Conceptual Sequence of Archive Data Recovery.</p>


The script executes a two-pronged strategy to ensure maximum data retrieval and media accessibility:

1.  **Granular Metadata Extraction (Dual Strategy):** This method guarantees capture of every descriptive field:

    * **Precision Targeting:** Focuses on specific HTML classes (`div.name`/`div.value`) common to professional catalogue platforms (e.g., AtoM).
    * **Robust Fallback:** Implements a search for standard HTML definition lists (`<dl>`, `<dt>`, `<dd>`) for any leftover or custom fields.

2.  **URL Negotiation and Media Retrieval:** This addresses the technical hurdle of downloading files hosted externally:

    * **Wayback Prefix Cleansing:** The script automatically strips the Wayback Machine's timestamp prefix from media links. This is the crucial step that prevents common **HTTP 403 Forbidden** errors, allowing the external utility, **`yt-dlp`**, to access the original media resource successfully.

***

## Prerequisites and Setup

* **Python 3.x**
* **Required Python Libraries:** `requests`, `beautifulsoup4`, `lxml`.
* **Media Downloader:** The external tool **`yt-dlp`** must be installed and accessible in your system's PATH.

### Installation

```bash
git clone https://github.com/josevelazquez/Wayback-Recovery-Script.git
cd Wayback-Recovery-Script
pip install requests beautifulsoup4 lxml
```

### Configuration

**The placeholders** in the `archival_harvester.py` script under the `--- Configuration Constants ---` section **must be edited** to point to your specific archived catalogue's URLs.
