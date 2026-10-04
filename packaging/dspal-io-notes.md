# dspal I/O notes

The first PDS I/O slice is deliberately text-only. Managed FB text libraries use strict host UTF-8 validation against CP037 and refuse records longer than the manifest LRECL. The current socket-reader path accepts the ASCII subset used by project source. Load-library member data is not treated as text.
