import digitalio
import board

i2c_power = digitalio.DigitalInOut(board.I2C_POWER)
i2c_power.switch_to_input()

print("##### i2c_power_disable.py has run")
