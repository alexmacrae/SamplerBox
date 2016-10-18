###############################
# Custom characters for the
# HD44780 16x2 LCD
###############################

# The HD44780 supports up to 8 custom characters(location 0 - 7).

# We can (kind of) cheat this by overwriting a location. Good for battery status or a clock.
# Not good for a custom font because overwriting A with B will then show all A characters as the new B
# UPDATE: have run into some issues with this method. Perhaps not feasible after all :(
#
# Write it to memory:
# lcd.create_char(location, bitmap)
# Display it:
# lcd.write_string(unichr(location))

block = (0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111)

battery_0 = (0b00100, 0b01110, 0b01010, 0b01010, 0b01010, 0b01010, 0b01010, 0b01110)
battery_20 = (0b00100, 0b01110, 0b01010, 0b01010, 0b01010, 0b01010, 0b01110, 0b01110)
battery_40 = (0b00100, 0b01110, 0b01010, 0b01010, 0b01010, 0b01110, 0b01110, 0b01110)
battery_60 = (0b00100, 0b01110, 0b01010, 0b01010, 0b01110, 0b01110, 0b01110, 0b01110)
battery_80 = (0b00100, 0b01110, 0b01010, 0b01110, 0b01110, 0b01110, 0b01110, 0b01110)
battery_100 = (0b00100, 0b01110, 0b01110, 0b01110, 0b01110, 0b01110, 0b01110, 0b01110)
battery_states = [battery_0, battery_20, battery_40, battery_60, battery_80, battery_100]

vload_0 = (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000)
vload_1 = (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111)
vload_2 = (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111, 0b11111)
vload_3 = (0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111, 0b11111, 0b11111)
vload_4 = (0b00000, 0b00000, 0b00000, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111)
vload_5 = (0b00000, 0b00000, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111)
vload_6 = (0b00000, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111)
vload_7 = (0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111)
vload_states = [vload_0, vload_1, vload_2, vload_3, vload_4, vload_5, vload_6, vload_7]

number_0 = (0b01110, 0b11011, 0b11011, 0b11011, 0b11011, 0b11011, 0b11011, 0b01110)
number_1 = (0b00010, 0b00110, 0b01110, 0b00110, 0b00110, 0b00110, 0b00110, 0b00110)
number_2 = (0b01110, 0b11011, 0b00011, 0b00110, 0b01100, 0b11000, 0b11111, 0b11111)
number_3 = (0b01110, 0b11011, 0b00011, 0b01110, 0b00011, 0b11011, 0b11011, 0b01110)
number_4 = (0b00011, 0b00111, 0b01111, 0b11011, 0b11111, 0b00011, 0b00011, 0b00011)
number_5 = (0b11111, 0b11000, 0b11110, 0b00011, 0b00011, 0b11011, 0b11111, 0b01110)
number_6 = (0b01110, 0b11011, 0b11000, 0b11110, 0b11011, 0b11011, 0b11111, 0b01110)
number_7 = (0b11111, 0b00011, 0b00110, 0b01100, 0b01100, 0b01100, 0b01100, 0b01100)
number_8 = (0b01110, 0b11011, 0b11011, 0b01110, 0b11011, 0b11011, 0b11011, 0b01110)
number_9 = (0b01110, 0b11011, 0b11011, 0b01111, 0b00011, 0b11011, 0b11111, 0b01110)
numbers = [number_0, number_1, number_2, number_3, number_4, number_5, number_6, number_7, number_8, number_9]

letter_A = (0b01110, 0b11011, 0b11011, 0b11111, 0b11111, 0b11011, 0b11011, 0b11011)
letter_L = (0b11000, 0b11000, 0b11000, 0b11000, 0b11000, 0b11000, 0b11111, 0b11111)
letter_E = (0b11111, 0b11111, 0b11000, 0b11110, 0b11110, 0b11000, 0b11111, 0b11111)
letter_X = (0b11011, 0b11011, 0b11011, 0b01110, 0b01110, 0b11011, 0b11011, 0b11011)
alex = [letter_A, letter_L, letter_E, letter_X]

voice_button_off = (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11111)
voice_button_on = (0b01110, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111)

arrow_right_01 = (0b00000, 0b11000, 0b10100, 0b10010, 0b10001, 0b10010, 0b10100, 0b11000)
arrow_right_02 = (0b00000, 0b11000, 0b11100, 0b10110, 0b10011, 0b10110, 0b11100, 0b11000)
arrow_right_03 = (0b00000, 0b11000, 0b11100, 0b11110, 0b11111, 0b11110, 0b11100, 0b11000)
arrow_right_04 = (0b00000, 0b01000, 0b01100, 0b01110, 0b01100, 0b01000, 0b00000, 0b00000)
arrow_right = [arrow_right_01, arrow_right_02, arrow_right_03]
