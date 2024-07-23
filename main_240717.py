import sys

import ujson
import utime
from machine import UART, Pin

sys.path.insert(0, './code_v2')
from code_v2.Motor import PicoGo

LOW_SPEED = 40
MEDIUM_SPEED = 60
HIGH_SPEED = 90


class PicoGoMobileRobot:
    """
    PicoGo Mobile Robot
    """

    def __init__(self):
        """
        
        """
        self.echo = Pin(15, Pin.IN)
        self.trig = Pin(14, Pin.OUT)
        self.motor = PicoGo()
        self.init_ultrasonic()
        self.uart = self.init_uart_for_bluetooth()
        self.led = Pin(25, Pin.OUT)

    def init_ultrasonic(self) -> None:
        """

        :return:
        """
        self.trig.off()
        self.echo.off()

    def init_uart_for_bluetooth(self):
        """

        :return:
        """
        uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
        return uart

    def control_onboard_led_blink(self) -> None:
        """

        :return:
        """
        self.led.off()
        utime.sleep(2)

        for i in range(4):
            self.led.toggle()
            utime.sleep(0.3)
        self.led.off()

    def test_start_motor(self) -> None:
        """
        
        :return: 
        """
        self.motor.forward(50)
        utime.sleep(2)

        self.motor.backward(50)
        utime.sleep(2)

        self.motor.left(30)
        utime.sleep(2)

        self.motor.right(30)
        utime.sleep(2)

        self.motor.stop()

    def calc_distance(self) -> float:
        """
        
        :return: 
        """
        self.trig.value(1)
        utime.sleep_us(10)
        self.trig.value(0)
        while (self.echo.value() == 0):
            pass
        ts = utime.ticks_us()
        while (self.echo.value() == 1):
            pass
        te = utime.ticks_us()
        distance = ((te - ts) * 0.034) / 2
        return distance

    def test_start_car(self) -> None:
        """

        :return:
        """
        for i in range(100 * 10000):
            distanc = self.calc_distance()
            if (distanc <= 30):
                # if randoself.motor.randint(0, 1):
                self.motor.backward(30)
                utime.sleep(100)
                self.motor.right(30)

                # else:
                # self.motor.left(35)
                # Ab.left()
            else:
                self.motor.forward(50)

            utime.sleep_ms(20)

    def read_uart(self):
        """

        :return:
        """
        command = self.uart.read()
        speed = 50

        def handle_forward(cmd, speed):
            if cmd == "Down":
                self.motor.forward(speed)
                self.uart.write("{\"State\":\"Forward\"}")
            elif cmd == "Up":
                self.motor.stop()
                self.uart.write("{\"State\":\"Stop\"}")

        def handle_backward(cmd, speed):
            if cmd == "Down":
                self.motor.backward(speed)
                self.uart.write("{\"State\":\"Backward\"}")
            elif cmd == "Up":
                self.motor.stop()
                self.uart.write("{\"State\":\"Stop\"}")

        def handle_left(cmd, speed):
            if cmd == "Down":
                self.motor.left(speed)
                self.uart.write("{\"State\":\"Left\"}")
            elif cmd == "Up":
                self.motor.stop()
                self.uart.write("{\"State\":\"Stop\"}")

        def handle_right(cmd, speed):
            if cmd == "Down":
                self.motor.right(speed)
                self.uart.write("{\"State\":\"Right\"}")
            elif cmd == "Up":
                self.motor.stop()
                self.uart.write("{\"State\":\"Stop\"}")

        def handle_speed(cmd):
            if cmd == "Low":
                self.uart.write("{\"State\":\"Low\"}")
                return LOW_SPEED
            elif cmd == "Medium":
                self.uart.write("{\"State\":\"Medium\"}")
                return MEDIUM_SPEED
            elif cmd == "High":
                self.uart.write("{\"State\":\"High\"}")
                return HIGH_SPEED
            return None

        def handle_led(cmd):
            if cmd == "on":
                self.led.value(1)
                self.uart.write("{\"State\":\"LED: ON\"}")
            elif cmd == "off":
                self.led.value(0)
                self.uart.write("{\"State\":\"LED: OFF\"}")

        if command is not None:
            print(command)
            self.uart.write(ujson.dumps(command))
            try:
                command_json = ujson.loads(command)
                print(command_json)

                for key, value in command_json.items():
                    if key == 'Forward':
                        handle_forward(value, speed)
                    elif key == 'Backward':
                        handle_backward(value, speed)
                    elif key == 'Left':
                        handle_left(value, LOW_SPEED)
                    elif key == 'Right':
                        handle_right(value, LOW_SPEED)
                    elif key in ('Low', 'Medium', 'High'):
                        new_speed = handle_speed(key)
                        if new_speed is not None:
                            speed = new_speed
                    elif key == 'LED':
                        handle_led(value)

            except Exception as e:
                self.uart.write(ujson.dumps({'State': f'Error {command}: {str(e)}'}))
                print(e)

    def start(self) -> None:
        self.control_onboard_led_blink()
        while True:
            self.read_uart()


if __name__ == '__main__':
    pgmr = PicoGoMobileRobot()
    pgmr.start()
