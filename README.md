# bcmImageTool
Broadcom Image Builder tool  

With this tool you can edit official firmwares of some modem router vendors like D-Link.  
This tool can change the kernel and the file system of an official firmware.  
It's better to flash the official firmware and then create a custom firmware to be sure your modem router is running a compatible CFE bootloader.  

My original goal was to create a docker image to compile the firmware provided on the [GPL](http://tsd.dlink.com.tw/downloads2008list.asp?OS=GPL) website.  
I tried it, but the GPL code provided is creating a firmware too big to fit in the flash and this resulted in a non working firmware.  
So I left this way ant decided to customize a working official firmware.

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

Tested on D-Link DSL-2750B D1 EU with firmware version 1.02

1) Flash original firmware  
Skip this step if your modem router is already running with the firmware version you are going to customize.  

1) Extract file system and kernel from the original firmware  
`./bcmImageTool.py split -i Original_FW.bin -d extract`  
This will create a folder named `extract` with `kernel` and `rootfs` files.  

2) Decompress file system  
`sudo binwalk -e extract/rootfs`  
Use sudo or `/dev` will be empty and you will make a corrupted custom firmware!  

3) Edit files inside `extract/_rootfs.extract/squashfs-root`  
You can edit `/etc/profile` to run code at startup.  

4) Compress file system  
`./mksquashfs extract/_rootfs.extract/squashfs-root extract/rootfs.new -be -noappend -all-root -b 65536`  
Use mksquashfs version 4.0 (2009/04/05) (precompiled binary is provided in this repo).  
(DSL-2750B uses SquashFS, but different hardware may have JFFS2 or CramFS file system).  
(Check the Block size and the Endianness too!).  

5) Rebuild image  
`./bcmImageTool.py merge -i Original_FW.bin -o Custom_FW.bin -k extract/kernel -r extract/rootfs.new`  
This will create a new firmware with the custom file system and the original kernel.  

6) Flash custom firmware  
Upgrade the firmware using Custom_FW.bin from the web interface like an official firmware.  

## Unbrick
My tool is NOT touching CFE bootloader, so if your modem router isn't working after flashing, don't worry!  
You can recover it reinstalling the official firmware.  
(This will reset your configurations to factory defaults)  
1) Power off the modem router
2) Press and keep pressed the reset button
3) Turn on the modem router
4) Keep pressed the reset button until power led becomes red
5) Connect a PC via LAN and set a static IP address like 192.168.1.5 (or 192.168.0.5)
7) Open browser to 192.168.1.1 (or 192.168.0.1)
8) Upload the official firmware

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
