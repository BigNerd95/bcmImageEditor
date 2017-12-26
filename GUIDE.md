## Examples
### Customize a firmware

Tested on D-Link DSL-2750B D1 EU with firmware version 1.02

1) Backup configurations  
In case you make a bad custon firmware and you have to unbrick your modem router, you can restore your configs.

2) Download the original firmware  
You can find the latest version of your modem on dlink's ftp servers (ftp://ftp.dlink.eu/Products/dsl/).  
For mine I used this one ftp://ftp.dlink.eu/Products/dsl/dsl-2750b/driver_software/DSL-2750B_HW_D1_EU_1.02_05292014_ITA.bin  

3) Flash the original firmware  
Skip this step if your modem router is already running with the firmware version you are going to customize.  

3) Extract file system and kernel from the original firmware  
`./bcmImageEditor.py split -i Original_FW.bin -d extract`  
This will create a folder named `extract` with `kernel` and `rootfs` files.  

4) Decompress file system  
`sudo binwalk -e extract/rootfs`  
Use sudo or `/dev` will be empty and you will make a corrupted custom firmware!  

5) Edit files inside `extract/_rootfs.extract/squashfs-root`  
You can edit `/etc/profile` to run code at startup.  

6) Compress file system  
`./mksquashfs extract/_rootfs.extract/squashfs-root extract/rootfs.new -be -noappend -all-root -b 65536`  
Use mksquashfs version 4.0 (2009/04/05) (precompiled binary is provided in this repo).  
(DSL-2750B uses SquashFS, but different hardware may have JFFS2 or CramFS file system).  
(Check the Block size and the Endianness too!).  

7) Rebuild image  
`./bcmImageEditor.py merge -i Original_FW.bin -o Custom_FW.bin -k extract/kernel -r extract/rootfs.new`  
This will create a new firmware with the custom file system and the original kernel.  

8) Flash custom firmware  
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
