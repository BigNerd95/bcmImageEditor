#!/usr/bin/env python3

# Broadcom lib by BigNerd95

import struct, crcmod.predefined
jamCRC = crcmod.predefined.mkCrcFun('jamcrc')

# Broadcom constants
IMAGE_BASE = 0xbfc00000
TAG_LEN = 256
RESERVED_LEN = 42

def toStr(data):
    return data.decode('ascii').rstrip('\0')

def toBytes(data):
    return bytes(str(data), 'ascii')


class Tag():
    def __init__(self, data):
        self.__fromBin__(data)

    def __fromBin__(self, data):
        fields = struct.unpack("4s20s14s6s16s2s10s12s10s12s10s12s10s4s32s"+str(RESERVED_LEN)+"s20s20s", data)
        # Text fields
        self.tagVersion = int(toStr(fields[0]))
        self.signature1 = toStr(fields[1])
        self.signature2 = toStr(fields[2])
        self.chipID     = int(toStr(fields[3]))
        self.boardID    = toStr(fields[4])
        self.bigEndian  = bool(int(toStr(fields[5])))
        self.imageLen   = int(toStr(fields[6]))
        self.cfeAddr    = int(toStr(fields[7]))
        self.cfeLen     = int(toStr(fields[8]))
        self.rootfsAddr = int(toStr(fields[9]))
        self.rootfsLen  = int(toStr(fields[10]))
        self.kernelAddr = int(toStr(fields[11]))
        self.kernelLen  = int(toStr(fields[12]))
        self.imageSeq   = toStr(fields[13])
        self.imageVer   = toStr(fields[14])
        self.reserved   = fields[15]
        # Binary fields
        self.imageToken = fields[16]
        self.tagToken   = fields[17]

        # Extract JamCRC from binary fields
        (self.imageCRC,
        self.rootfsCRC,
        self.kernelCRC,
        _, _)           = self.endianUnpack("5I", self.imageToken)

        (self.tagCRC,
        _, _, _, _)     = self.endianUnpack("5I", self.tagToken)

    def endianPack(self, format, *fields):
        if self.bigEndian:
            return struct.pack(">" + format, *fields)
        else:
            return struct.pack("<" + format, *fields)

    def endianUnpack(self, format, data):
        if self.bigEndian:
            return struct.unpack(">" + format, data)
        else:
            return struct.unpack("<" + format, data)

    def updateTagCRC(self):
        self.tagCRC = jamCRC(self.__toBin__()[:-20])

    def __toBin__(self):
        self.imageToken = self.endianPack("5I",
            self.imageCRC,
            self.rootfsCRC,
            self.kernelCRC,
            0,
            0
        )

        self.tagToken = self.endianPack("5I",
            self.tagCRC,
            0,
            0,
            0,
            0
        )

        bindata = struct.pack("4s20s14s6s16s2s10s12s10s12s10s12s10s4s32s"+str(RESERVED_LEN)+"s20s20s",
            toBytes(self.tagVersion)[:3],
            toBytes(self.signature1)[:19],
            toBytes(self.signature2)[:13],
            toBytes(self.chipID)[:5],
            toBytes(self.boardID)[:15],
            toBytes("1" if self.bigEndian else "0")[:1],
            toBytes(self.imageLen)[:9],
            toBytes(self.cfeAddr)[:11],
            toBytes(self.cfeLen)[:9],
            toBytes(self.rootfsAddr)[:11],
            toBytes(self.rootfsLen)[:9],
            toBytes(self.kernelAddr)[:11],
            toBytes(self.kernelLen)[:9],
            toBytes(self.imageSeq)[:3],
            toBytes(self.imageVer)[:31],
            self.reserved,
            self.imageToken,
            self.tagToken
        )
        return bindata

    def __str__(self):
        res_bytes = RESERVED_LEN - self.reserved.count(0)

        return "Tag Version:        " + str(self.tagVersion)       + "\n" \
               "Signature 1:        " + str(self.signature1)       + "\n" \
               "Signature 2:        " + str(self.signature2)       + "\n" \
               "Chip ID:            " + str(self.chipID)           + "\n" \
               "Board ID:           " + str(self.boardID)          + "\n" \
               "Big Endian flag:    " + str(self.bigEndian)        + "\n" \
               "Total Image Length: " + str(self.imageLen)         + " bytes\n" \
               "CFE Address:        " + str(hex(self.cfeAddr))     + "\n" \
               "CFE Length:         " + str(self.cfeLen)           + " bytes\n" \
               "RootFS Address:     " + str(hex(self.rootfsAddr))  + "\n" \
               "RootFS Length:      " + str(self.rootfsLen)        + " bytes\n" \
               "Kernel Address:     " + str(hex(self.kernelAddr))  + "\n" \
               "Kernel Length:      " + str(self.kernelLen)        + " bytes\n" \
               "Image sequence:     " + str(self.imageSeq)         + "\n" \
               "Image version:      " + str(self.imageVer)         + "\n" \
               "Reserved:           " + str(res_bytes)             + " not null bytes\n" \
               "Image jamCRC:       " + str(hex(self.imageCRC))    + "\n" \
               "RootFS jamCRC:      " + str(hex(self.rootfsCRC))   + "\n" \
               "Kernel jamCRC:      " + str(hex(self.kernelCRC))   + "\n" \
               "Tag jamCRC:         " + str(hex(self.tagCRC))      + "\n"
