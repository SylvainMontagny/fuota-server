#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:         Redunduncy fragment generator for Data Fragmented Block Transmission
# Autor:        Antoine AUGAGNEUR
# Date:         May, 2022
# Script from:  Application Note AN5554, STMicroelectronics

# =====================================================
# Imports
# =====================================================
import os
import sys
import logging
import socket
import binascii
import math
from datetime import datetime
from time import sleep
import csv
import subprocess

# for UI
from tkinter import *
from tkinter import ttk, filedialog
import tkinter
from tkinter.filedialog import askopenfile
from turtle import delay
#from typing_extensions import Self


# =====================================================
# Global variables
# =====================================================
logger = logging.getLogger('__name__')
filepath = ""
initalsize = 1

# =====================================================
# User inputs
# =====================================================

# Global information
print("\n")
print("USMB - LoRaWAN Fragmented Data Block Tool")
print("(C) Antoine AUGAGNEUR, 2022 \n")
print("Steps:")
print("       1/ Precise the mode you want: [0] Interop (arbitrary data with adjustable fragment settings)")
print("                                     [1] File    (.sfb file to send via FUOTA process)")
print("       2/ Give the fragmentation settings")
print("       3/ Save the generated .sfb and .csv files \n")
input("Presse ENTER to continue... \n")

# Get the mode
mode_input = int(input("Desired mode (Interop [0] or File [1]):    "))

# Get settings/data depending on mode

# --> INTEROP MODE
if (mode_input == 0):        
    test_matlab = True
    test_interop = False
    print("> Interop mode.")
    fs_input = int(input("Set [fragment size] in bytes:              "))
    nf_input = int(input("Set the [number of frag]:                  "))
    #rd_input = int(input("Set [number of redundancy frag] in bytes:  "))       # commented because not used

# --> FILE MODE
elif (mode_input == 1):     
    test_matlab = False
    test_interop = False
    print("> File mode.")
    fs_input = int(input("Set [fragment size] in bytes (max 112):    "))        # 115 bytes in SF9. Fragment command = 3-bytes header + 112-bytes data = 115-bytes data fragment command
    #rd_input = int(input("Set [number of redundancy frag] in bytes:  "))       # commented because not used
    if fs_input > 112:
        fs_input = 112      # it cannot be more than 112 (bcause max payload is: 115 bytes = 3-bytes header + 112-bytes data fragment)
    
    # File choice
    print("> Chose your file.")
    tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
    file = filedialog.askopenfile(mode='r')
    if file:
        filepath = os.path.abspath(file.name)
        initalsize = os.path.getsize(filepath)
        print("File: " + filepath + "| File size: " + str(initalsize) + " bytes")
    else:
        print("Something went wrong")
        exit()

# --> NO MODE
else:
    print("Wrong input. Try again.")
    exit()

# settings assignment
fec_algo_version = 1
if test_interop:
    input_file = 'Interoptest_file_1.bin'
    fragment_size = 5
    redundancy = 5
else:
    input_file = filepath           # 'LoRaWAN_End_Node.sfb'
    fragment_size = fs_input        # 112
    # redundancy = rd_input           # 72



# =====================================================
# prbs23 function
# =====================================================
def prbs23(start):
    '''The prbs23() function implements a PRBS generator with 2^23 period.
    standard implementation of a 23bit prbs generator'''
    x = start
    b0 = x & 1
    b1 = int((x & 32) / 32)
    x = (x >> 1) | ((b0 ^ b1) << 22)
    return x

# =====================================================
# matrix_line function
# =====================================================
def matrix_line(N, M):
    '''the matrix_line function generating a parity check vector:
    this function returns line N of the MxM parity matrix'''
    nb_coeff = 0
    line = [0]*M

    # if M is a power of 2
    if (M & (M - 1) == 0) and M != 0:
        pow2 = 1
    else:
        pow2 = 0
    # initialize the seed differently for each line
    x = 1 + (1001 * (N + 1))

    # will generate a line with M / 2 bits set to 1 (50 % )
    while (((fec_algo_version == 2) and (line.count(1) < math.floor(M / 2))) or
        ((fec_algo_version == 1) and (nb_coeff < math.floor(M / 2)))):
        r = math.pow(2, 16)
        # this can happen if m=1, in that case just try again with a different random number
        while r >= M:
            x = prbs23(x)
            # bit number r of the current line will be switched to 1
            r = x % (M + pow2)

        # set to 1 the column which was randomly selected
        line[r] = 1
        nb_coeff += 1
    return line


# =====================================================
# MAIN PROGRAMM
# =====================================================
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(message)s', level=logging.DEBUG)
    output_file = os.path.splitext(input_file)[0] + '_coded' + os.path.splitext(input_file)[1]

    uncoded_frag = []
    # nb of bytes per fragment
    print("")
    if test_matlab:
        print("> Generated file:")
        fragment_size = fs_input
        nb_fragment = nf_input
        for i in range(nb_fragment):
            buffer = ''
            for j in range(fragment_size):
                buffer += '{:02X}'.format((i*fragment_size+j) % 256)
            print(buffer)
            uncoded_frag.append(buffer)
    else:
    # Read the binary file and convert into fragments list of size <fragment_size>
        try:
            with open(input_file, "rb") as f:
                while bytes_str := f.read(fragment_size):
                    uncoded_frag.extend([binascii.hexlify(bytes_str).decode()])
        except FileNotFoundError as e:
            logger.error(e)
            exit(1)
        # Get the number of fragments into the binary file
        nb_fragment = len(uncoded_frag)
        # 0-Padding of the last fragments
        uncoded_frag[-1] += '0'*(fragment_size*2-len(uncoded_frag[-1]))
    
    # generate a coded array based on uncoded content
    coded_frag = []
    #logger.debug('Matrix:')
    for y in range(nb_fragment):
        s = '0'*(2 * fragment_size)
        # line y of M x M matrix
        A = matrix_line(y, nb_fragment)
        #logger.debug('{:03}: {} - {:03}'.format(y + 1, A, A.count(1)))

        for x in range(nb_fragment):
            # if bit x is set to 1 then xor the corresponding fragment
            if A[x] == 1:
                s = '{:X}'.format(int(s, 16) ^ int(uncoded_frag[x], 16))

        # prevent Odd-length string
        s = '0'*((fragment_size * 2) - len(s)) + s

        # save coded fragment
        coded_frag.extend([s])


    # Display the uncoded and coded fragments (only in interop mode)
    if test_matlab:
        print("")
        print("> Uncoded fragments:")
        for num, frag in enumerate(uncoded_frag, start=1):
            #logger.debug('{:03}: {}'.format(num, frag.upper()))
            print('{:03}: {}'.format(num, frag.upper()))
        print("> Coded fragments:")
        for num, frag in enumerate(coded_frag, start=1):
            #logger.debug('{:03}: {}'.format(num, frag.upper()))
            print('{:03}: {}'.format(num, frag.upper()))


    # cr
    if test_matlab == False:
        print("")
        print("> Generated file information:")
        print(" -- Initial file size:            " + str(initalsize) + " bytes")
        print(" -- Fragment size:                " + str(fs_input) + " bytes")
        print(" -- Number of uncoded fragment:   " + str(nb_fragment))  
        print(" -- Number of coded fragment:     " + str(nb_fragment) + " /!\ The script gives 100 %" + " of redundancy fragments by default. However, your FUOTA-Server or your device settings may only allow a tiny percentage.")
        print(" -- Total number of fragment:     " + str(2*nb_fragment))
        padding = nb_fragment*fs_input - initalsize
        time_dutycycle = round(nb_fragment/530,1)            # in hours -- 10% max duty cycle in SF9, 869.525MHz / EU868  => 530 msg/hour
        time_fairpolicy = round(nb_fragment/44,1)            # in days  -- fair access policy in SF9 EU868 => 44 msg/day (TTN ONLY)
        print(" -- Needed padding:               " + str(padding) + " bytes")
        print(" -- Estimate FUOTA session time:  " + str(time_dutycycle) + " hours (with duty-cycle respected, in SF9 869.525MHz / EU868 -- 530 msg/hour)")
        #print(" -- Estimate FUOTA session time:  " + str(time_dutycycle) + " days (with fair access policy respected, in SF9 EU868 -- 44 msg/day)")

    # get the folder path to register the files
    print("")
    if(int(input("Save the file ? (Yes: [1] / No: [0]): ")) == 1):
        tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
        path = filedialog.askdirectory()
        if path != "":
            print("Choses folder: " + path)
        else:
            print("Something went wrong")
            exit()
    else:
        print("Exit...")
        exit()

    
    # SFB file writting --------------------------------------------------------------------------------------------------------
    print("")
    if test_matlab:
        output_file_sfb = path + "/interop_file.sfb"
    else:
        output_file_sfb = path + "/YourFirmware_fragmented.sfb"

    with open(output_file_sfb, "wb") as f:
        for num, frag in enumerate(uncoded_frag, start=1):
            #logger.debug('{:03}: {}'.format(num, frag.upper()))
            f.write(binascii.unhexlify(frag.encode()))
        for num, frag in enumerate(coded_frag, start=1):
            #logger.debug('{:03}: {}'.format(num, frag.upper()))
            f.write(binascii.unhexlify(frag.encode()))
    print('> Output file: {} | File size: {} bytes'.format(output_file_sfb, os.path.getsize(output_file_sfb)))
    # --------------------------------------------------------------------------------------------------------------------------
    # CSV file writting --------------------------------------------------------------------------------------------------------
    if test_matlab:
        output_file_csv = path + "/interop_file.csv"
    else:
        output_file_csv = path + "/YourFirmware_fragmented.csv"

    with open(output_file_csv, "w", newline='') as f:
        for num, frag in enumerate(uncoded_frag, start=1):
            buffer = str(frag.upper())
            buffer_modified = ''
            for i in range(fragment_size*2):
                buffer_modified += buffer[i]
                if ((i % 2) != 0) and (i>0) and (i<(fragment_size*2)-1):
                    buffer_modified += ','
            f.write(buffer_modified+"\n")
        for num, frag in enumerate(coded_frag, start=1):
            buffer = str(frag.upper())
            buffer_modified = ''
            for i in range(fragment_size*2):
                buffer_modified += buffer[i]
                if ((i % 2) != 0) and (i>0) and (i<(fragment_size*2)-1):
                    buffer_modified += ','
            f.write(buffer_modified+"\n")
    print('> Output file: {} | File size: {} bytes'.format(output_file_csv, os.path.getsize(output_file_csv)))
    # ------------------------------------------------------------------------------------------------------------

    # end
    print("")
    input("Presse ENTER to exit...")
    exit()