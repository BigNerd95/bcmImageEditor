#!/usr/bin/env python3

# Broadcom Image Tools by BigNerd95

import sys, os, struct, Broadcom
from argparse import ArgumentParser, FileType

def get_data(input_file, start, length):
    input_file.seek(start, 0)
    return input_file.read(length)

def create_write_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)

##################
# main functions #
##################

def merge(input_file, rootfs_file, kernel_file, output_file):
    print("** Broadcom Image merge **")
    header = get_data(input_file, 0, Broadcom.TAG_LEN)
    tag = Broadcom.Tag(header)
    print("Original firmware")
    print(tag)
    print()

    original_cfe  = get_data(input_file, Broadcom.TAG_LEN, tag.cfeLen) # may be empty
    custom_rootfs = rootfs_file.read()
    custom_kernel = kernel_file.read()
    newImage = original_cfe + custom_rootfs + custom_kernel

    # update header fields
    tag.imageLen   = len(newImage)
    tag.rootfsLen  = len(custom_rootfs)
    tag.kernelAddr = tag.rootfsAddr + len(custom_rootfs)
    tag.kernelLen  = len(custom_kernel)
    tag.imageCRC   = Broadcom.jamCRC(newImage)
    tag.rootfsCRC  = Broadcom.jamCRC(custom_rootfs)
    tag.kernelCRC  = Broadcom.jamCRC(custom_kernel)
    tag.updateTagCRC()

    print("Custom firmware")
    print(tag)

    output_file.write(tag.__toBin__())
    output_file.write(newImage)

    input_file.close()
    rootfs_file.close()
    kernel_file.close()
    output_file.close()

def split(input_file, directory):
    print("** Broadcom Image split **")
    header = get_data(input_file, 0, Broadcom.TAG_LEN)
    tag = Broadcom.Tag(header)

    path = os.path.join(directory, '')
    if os.path.exists(path):
        print("Directory", os.path.basename(path) , "already exists, cannot split!")
        return

    #cfe    = get_data(input_file, Broadcom.TAG_LEN, tag.cfeLen)
    rootFS = get_data(input_file, Broadcom.TAG_LEN + tag.cfeLen, tag.rootfsLen)
    kernel = get_data(input_file, Broadcom.TAG_LEN + tag.cfeLen + tag.rootfsLen, tag.kernelLen)

    #create_write_file(path + 'cfe', cfe)
    create_write_file(path + 'rootfs', rootFS)
    create_write_file(path + 'kernel', kernel)

    input_file.close()


def info(input_file):
    print("** Broadcom Image info **")
    header = get_data(input_file, 0, Broadcom.TAG_LEN)
    tag = Broadcom.Tag(header)
    print(tag)
    input_file.close()

def parse_cli():
    parser = ArgumentParser(description='** Broadcom Image Tools by BigNerd95 **')
    subparser = parser.add_subparsers(dest='subparser_name')

    infoParser = subparser.add_parser('info', help='Print Tag (header) info')
    infoParser.add_argument('-i', '--input', required=True, metavar='INPUT_FILE', type=FileType('rb'))

    splitParser = subparser.add_parser('split', help='Extract rootfs and kernel from image')
    splitParser.add_argument('-i', '--input', required=True, metavar='INPUT_FILE', type=FileType('rb'))
    splitParser.add_argument('-d', '--directory', required=True, metavar='EXTRACT_DIRECTORY')

    mergeParser = subparser.add_parser('merge', help='Create a new image with custom rootfs and kernel using the original image as base')
    mergeParser.add_argument('-i', '--input',  required=True, metavar='INPUT_FILE', type=FileType('rb'))
    mergeParser.add_argument('-r', '--rootfs', required=True, metavar='ROOTFS_FILE', type=FileType('rb'))
    mergeParser.add_argument('-k', '--kernel', required=True, metavar='KERNEL_FILE', type=FileType('rb'))
    mergeParser.add_argument('-o', '--output', required=True, metavar='OUTPUT_FILE', type=FileType('wb'))

    if len(sys.argv) < 2:
        parser.print_help()

    return parser.parse_args()

def main():
    args = parse_cli()
    if args.subparser_name == 'info':
        info(args.input)
    elif args.subparser_name == 'split':
        split(args.input, args.directory)
    elif args.subparser_name == 'merge':
        merge(args.input, args.rootfs, args.kernel, args.output)

if __name__ == '__main__':
    main()
