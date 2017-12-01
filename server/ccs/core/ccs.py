import argparse
import logging
import os
import signal
import subprocess
import time
from threading import Thread

from . import api, config, settings
from .color import BLACK
from ccs import logger
from ccs.led.led import Led
from ccs.lcd.lcd import Lcd

LED_THREAD_PAUSE = 0.05
LCD_THREAD_PAUSE = 0.1
KEEPALIVE_THREAD_PAUSE = 1.0


class CaseControlServer:
    def __init__(self, args):
        self._run = True
        self._keepalive_up = True

        if args.debug:
            logger.setLevel(logging.DEBUG)

        # Init config and settings
        if not os.path.exists(args.working_dir):
            os.makedirs(args.working_dir)
        cfg = config.load(args.working_dir)
        settings.init(args.working_dir)

        # Init the LED/LCD handlers
        led = Led(cfg['led_socket'])
        logger.debug("Initialized LED")
        lcd = Lcd(cfg['lcd_socket'], cfg['lcd_width'], cfg['lcd_height'])
        logger.debug("Initialized LCD")

        keepalive_hosts = cfg['keepalive_hosts']
        keepalive_timeout = cfg['keepalive_timeout']

        # Add background threads/processes to be run
        self._threads = [
            Thread(target=self._led_thread, name='LED-Thread', args=(led,)),
            Thread(target=self._lcd_thread, name='LCD-Thread', args=(lcd,)),
            Thread(target=self._keepalive_thread, name='Keepalive-Thread', daemon=True,
                   args=(keepalive_hosts, keepalive_timeout)),
            Thread(target=api.app.run, daemon=True, kwargs={'host': '0.0.0.0'}),
        ]

        signal.signal(signal.SIGTERM, lambda sig, frame: self.stop())  # Catch SIGTERM

    def run(self):
        # Start the helper threads, then launch the REST API
        try:
            logger.debug("Starting threads...")
            for thread in self._threads:
                thread.start()
            logger.debug("Started threads, now starting Flask...")
            logger.debug("Started Flask")

            self._wait()  # Wait for something to die
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()  # Shut down every thread/process

    def _wait(self):
        for thread in self._threads:
            if not thread.daemon:
                thread.join()

    def stop(self):
        # Stop, if this hasn't already been called once
        if self._run:
            logger.info("Stopping...")
            self._run = False

    def _led_thread(self, led):
        """
        @brief      A thread that periodically updates the case LEDs based on the current settings.
        """
        try:
            led.open()
            while self._run:
                if self._keepalive_up:
                    color = settings.get('led.mode').get_color(settings)
                else:
                    color = BLACK
                led.set_color(color)
                time.sleep(LED_THREAD_PAUSE)
            logger.debug("LED thread stopped")
        finally:
            self.stop()
            led.stop()

    def _lcd_thread(self, lcd):
        """
        @brief      A thread that periodically updates the case LEDs based on the current settings.
        """
        try:
            lcd.open()
            while self._run:
                if self._keepalive_up:
                    mode = settings.get('lcd.mode')
                    text = mode.get_text(settings)
                    if settings.get('lcd.link_to_led'):  # Special setting to use LED color for LCD
                        mode = settings.get('led.mode')
                    color = mode.get_color(settings)
                else:
                    text = ''
                    color = BLACK

                lcd.set_text(text)
                lcd.set_color(color)
                time.sleep(LCD_THREAD_PAUSE)
            logger.debug("LCD thread stopped")
        finally:
            self.stop()
            lcd.stop()

    def _keepalive_thread(self, hosts, timeout):
        # No hosts given, don't even bother
        if not hosts:
            return

        def ping(host):
            try:
                subprocess.check_call(['ping', '-c', '1', '-W', str(timeout), host],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                return False
        try:
            while self._run:
                alive = any(ping(host) for host in hosts)
                if alive != self._keepalive_up:
                    logger.info(f"Keepalive host(s) went {'up' if alive else 'down'}")
                    self._keepalive_up = alive
                time.sleep(KEEPALIVE_THREAD_PAUSE)
        finally:
            self.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('working_dir', nargs='?', default='.',
                        help="Directory to store settings, config, etc.")
    parser.add_argument('--debug', '-d', action='store_true', help="Enable debug mode")
    args = parser.parse_args()

    c = CaseControlServer(args)
    c.run()