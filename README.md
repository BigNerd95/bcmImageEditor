# bcmImageTool
Broadcom Image Builder tool

## Tag (header) structure
| Size (byte)  | Type | Name | Description |
| :----------: | ---- | ---- | ------- |
|  4 | String | Tag Version | Eg: 6 |
| 20 | String | Signiture 1 | Text line for company info |
| 14 | String | Signiture 2 | Additional info (can be version number) |
|  6 | String | Chip ID |  |
| 16 | String | Board ID |  |
|  2 | String | Big Endian flag | 1 = big, 0 = little |
| 10 | String | Total Image Length | The sum of all the following length |
| 12 | String | CFE Address | CFE starting address (if non zero) |
| 10 | String | CFE Length | CFE size in clear ASCII text (if non zero) |
| 12 | String | RootFS Address | Filesystem starting address (if non zero) |
| 10 | String | RootFS Length | Filesystem size in clear ASCII text (if non zero) |
| 12 | String | Kernel Address | Kernel starting address (if non zero) |
| 10 | String | Kernel Length | Kernel size in clear ASCII text (if non zero) |
|  4 | String | Image Sequence | Incrments everytime an image is flashed (?) |
| 74 | None | Reserved | Reserved for later use |
| 20 | String | Image Validation Token | JamCRC of: total image, rootFS, kernel |
| 20 | String | Tag Validation Token | JamCRC of Tag from Tag Version to the end of Image Validation Token |
