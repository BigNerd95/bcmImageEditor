# bcmImageTool
Broadcom Image Builder tool

## Usage
### Info  
Show image info    
`./bcmImageTool.py info -i DSL-2750B.bin`

### Split  
Extract rootfs and kernel from an image     
`./bcmImageTool.py split -i DSL-2750B.bin -d extract`

### Merge
Create a new image with custom rootfs and kernel     
`./bcmImageTool.py merge -i DSL-2750B.bin -o Custom-2750B.bin -r extract/rootfs -k extract/kernel`

## Examples
### Customize a firmware
```
# Extract file system
./bcmImageTool.py split -i Original_FW.bin -d extract
binwalk -e extract/rootfs

# Edit files inside extract/_rootfs.extract/squashfs-root

# Rebuild image
sudo ./makeDevs extract/_rootfs.extract/squashfs-root
./mksquashfs extract/_rootfs.extract/squashfs-root extract/rootfs.new -be -noappend -all-root -b 65536
./bcmImageTool.py merge -i Original_FW.bin -o Custom_FW.bin -k extract/kernel -r extract/rootfs.new
```

## Firmware structure
| Size (byte)  | Name | Description |
| :----------: | ---- | ------- |
| 256 | Tag (header) | Described below |
| CFE Length in Tag | CFE | May not be present |
| RootFS Length in Tag | Root File System | SquashFS, CramFS or Jffs2 |
| Kernel Length in Tag | Kernel | LZMA compressed kernel |

## Tag (header) structure
| Size (byte)  | Type | Name | Description |
| :----------: | ---- | ---- | ------- |
|  4 | String | Tag Version | Eg: 6 |
| 20 | String | Signiture 1 | Text line for company info, Eg: Broadcom Corporatio |
| 14 | String | Signiture 2 | Additional info (can be version number), Eg: ver. 2.0 |
|  6 | String | Chip ID | Eg: 6318 |
| 16 | String | Board ID | Eg: AW5200U |
|  2 | String | Big Endian flag | 1 = big, 0 = little |
| 10 | String | Total Image Length | The sum of all the following length |
| 12 | String | CFE Address | CFE starting address (if non zero) |
| 10 | String | CFE Length | CFE size in clear ASCII text (if non zero) |
| 12 | String | RootFS Address | Filesystem starting address (if non zero) |
| 10 | String | RootFS Length | Filesystem size in clear ASCII text (if non zero) |
| 12 | String | Kernel Address | Kernel starting address (if non zero) |
| 10 | String | Kernel Length | Kernel size in clear ASCII text (if non zero) |
|  4 | String | Image Sequence | Incrments everytime an image is flashed (?) |
| 32 | String | Image Version | Eg: 4127DSL-2750_EU1491125 |
| 42 | None | Reserved | Reserved for later use |
| 20 | Byte Array | Image Validation Token | JamCRC of: total image, rootFS, kernel |
| 20 | Byte Array | Tag Validation Token | JamCRC of Tag from Tag Version to the end of Image Validation Token |
