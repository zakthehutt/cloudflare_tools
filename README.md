# Cloudflare API Tools
Contributors: zakthehutt, wako104
<br/><br/>
Tags: DNS, Cloudflare API
<br/>
Requires: Python3, python-cloudflare wrapper

## Description
These Cloudflare API tools simplify applying changes across zones within your Cloudflare account.

## Versions:

#### 1.2 | May 22nd, 2024
* Domain Import Tool: This tool uses two files (TXT) to import domains in bulk, insert domains on their own line in the domains.txt file and define your records in the dns_records.txt file using JSON formatting.

#### 1.1 | May 10th, 2024
* Find and Replace: Uses a defined record to alter another record within all matching zones.

#### 1.0 | May 9th, 2024 
* ADD DMARC: Allows you to search across all zones and add a DMARC where any are missing.
* UPDATE CNAME: Searches for an existing CNAME record in all zones and replaces the content with user-defined content.
