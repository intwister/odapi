#!/usr/bin/env python
# vim: set fileencoding=utf-8 expandtab shiftwidth=4 tabstop=4 softtabstop=4:

# A library for controlling TM1638 displays from a Raspberry Pi
# Based on original work in C from https://code.google.com/p/tm1638-library/
# Converted to python by Jacek Fedorynski <jfedor@jfedor.org> (common cathode)
# Converted for TM1638 common anode by John Blackmore <john@johnblackmore.com>
# Converted for common cathode with addons from John

import RPi.GPIO as GPIO
from time import sleep
import re

GPIO.setwarnings(False) # suppresses warnings on RasPi


class TM1638(object):

    FONT = {
      '%': 0b00000000, # (37)   %
      '*': 0b00000000, # (42)   *
      '+': 0b00000000, # (43)   +
      ',': 0b00000100, # (44)   ,
      '-': 0b01000000, # (45)   -
      '.': 0b10000000, # (46)   .
      '0': 0b00111111, # (48)   0
      '1': 0b00000110, # (49)   1
      '2': 0b01011011, # (50)   2
      '3': 0b01001111, # (51)   3
      '4': 0b01100110, # (52)   4
      '5': 0b01101101, # (53)   5
      '6': 0b01111101, # (54)   6
      '7': 0b00100111, # (55)   7
      '8': 0b01111111, # (56)   8
      '9': 0b01101111, # (57)   9
      'A': 0b01110111, # (65)   A
      'B': 0b01111111, # (66)   B
      'C': 0b00111001, # (67)   C
      'D': 0b00111111, # (68)   D
      'E': 0b01111001, # (69)   E
      'F': 0b01110001, # (70)   F
      'G': 0b00111101, # (71)   G
      'H': 0b01110110, # (72)   H
      'I': 0b00000110, # (73)   I
      'J': 0b00011111, # (74)   J
      'K': 0b01110101, # (75)   K
      'L': 0b00111000, # (76)   L
      'M': 0b01010101, # (77)   M
      'N': 0b00110111, # (78)   N
      'O': 0b00111111, # (79)   O
      'P': 0b01110011, # (80)   P
      'Q': 0b01100111, # (81)   Q
      'R': 0b00110001, # (82)   R
      'S': 0b01101101, # (83)   S
      'T': 0b01111000, # (84)   T
      'U': 0b00111110, # (85)   U
      'V': 0b00101010, # (86)   V
      'W': 0b00011101, # (87)   W
      'X': 0b01110110, # (88)   X
      'Y': 0b01101110, # (89)   Y
      'Z': 0b01011011, # (90)   Z
      ' ': 0b00000000
    }

    def __init__(self, dio, clk, stb, sleep_time=0.001):
        self.dio = dio
        self.clk = clk
        self.stb = stb
        self.sleep_time = sleep_time

    def enable(self, intensity=7):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dio, GPIO.OUT)
        GPIO.setup(self.clk, GPIO.OUT)
        GPIO.setup(self.stb, GPIO.OUT)

        GPIO.output(self.stb, True)
        sleep(self.sleep_time)
        GPIO.output(self.clk, True)
        sleep(self.sleep_time)

        self.send_command(0x40)
        self.send_command(0x80 | 8 | min(7, intensity))

        GPIO.output(self.stb, False)
        sleep(self.sleep_time)
        self.send_byte(0xC0)
        for i in range(16):
            self.send_byte(0x00)
        GPIO.output(self.stb, True)
        sleep(self.sleep_time)

    def send_command(self, cmd):
        GPIO.output(self.stb, False)
        sleep(self.sleep_time)
        self.send_byte(cmd)
        GPIO.output(self.stb, True)
        sleep(self.sleep_time)

    def send_data(self, addr, data):
        self.send_command(0x44)
        GPIO.output(self.stb, False)
        sleep(self.sleep_time)
        self.send_byte(0xC0 | addr)
        self.send_byte(data)
        GPIO.output(self.stb, True)
        sleep(self.sleep_time)

    def send_byte(self, data):
        for i in range(8):
            GPIO.output(self.clk, False)
            sleep(self.sleep_time)
            GPIO.output(self.dio, (data & 1) == 1)
            sleep(self.sleep_time)
            data >>= 1
            GPIO.output(self.clk, True)
            sleep(self.sleep_time)

    def set_led(self, n, color):
        self.send_data((n << 1) + 1, color)

    def send_char(self, pos, data, dot=False):
        self.send_data(pos << 1, data | (128 if dot else 0))

    def set_digit(self, pos, digit, dot=False):
        for i in range(0, 6):
            self.send_char(i, self.get_bit_mask(pos, digit, i), dot)
    
    def get_bit_mask(self, pos, digit, bit):
        return ((self.FONT[digit] >> bit) & 1) << pos

    def display_line(self, text, dot_indexes, print_forward=False):
        text += " "*(8-len(text))
        
        start = 7
        end = -1
        increment = -1 
        
        if print_forward:
            start = 0
            end = 8
            increment = 1
        
        for i in range(start, end, increment):
            if i in dot_indexes:
                self.send_char(i, self.FONT[text[i]] | 0b10000000)
            else:
                self.send_char(i, self.FONT[text[i]])

    def remove_supported_characters(self, text):
        supported_characters = "".join(self.FONT.keys())

        return re.sub(r"[^" + supported_characters + "]", "", text)

    def set_text(self, text, scrolling=False, print_forward=False):
        text = text.upper()
        text = self.remove_supported_characters(text)
        print text
        buffer = ""
        dot_positions = list()

        pos = -1
        for char in text:
            if char == ".":
                dot_positions[pos] = True
            else:
                buffer += char
                dot_positions.append(False)

        end = len(buffer)-7
        if not scrolling:
            end = 1

        for i in range(0, end):
            dot_indexes = set(i for i, v in enumerate(dot_positions[i : i+8]) if v)
            self.display_line(buffer[i : i+8], dot_indexes, print_forward)

    def scroll_text(self, text, print_forward=False):
        self.set_text(text, scrolling=True, print_forward=print_forward)

    def receive(self):
        temp = 0
        GPIO.setup(self.dio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for i in range(8):
            temp >>= 1
            GPIO.output(self.clk, False)
            if GPIO.input(self.dio):
                temp |= 0x80
            GPIO.output(self.clk, True)
        GPIO.setup(self.dio, GPIO.OUT)
        return temp

    def get_buttons(self):
        keys = 0
        GPIO.output(self.stb, False)
        self.send_byte(0x42)
        for i in range(4):
            keys |= self.receive() << i
        GPIO.output(self.stb, True)
        return keys

    def rotate_bits(self, num):
#        for i in range(0, 4):
#            num = self.rotr(num, 8)
        return num

    def rotr(self, num, bits):
        num &= (2**bits-1)
        bit = num & 1
        num >>= 1
        if bit:
            num |= (1 << (bits-1))
        return num
