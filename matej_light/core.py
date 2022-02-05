import requests
from requests.exceptions import ConnectTimeout, ConnectionError
import json

KELVIN_MIN = 3000
KELVIN_MAX = 5000

TIMEOUT = 2.0


def map_val(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def clip(x, x_min, x_max):
    return max(x_min, min(x, x_max))


class MatejLightException(Exception):
    pass


class MatejLight:

    def __init__(self, ip):
        self.ip = ip
        self.status = {"brightness": 0,
                       "temperature": KELVIN_MIN,
                       "aux_rgb": (0, 0, 0),
                       "power": 0}
        self.post_url = "http://" + self.ip + "/chngConfig"
        self.get_url = "http://" + self.ip + "/getConfig"
        self.status_before_off = self.status

    @staticmethod
    def percent_warm_2_kelvin(percent):
        k = map_val(percent, 0, 100, KELVIN_MAX, KELVIN_MIN)
        return clip(k, KELVIN_MIN, KELVIN_MAX)

    @staticmethod
    def kelvin_2_percent_warm(kelvin):
        p = map_val(kelvin, KELVIN_MIN, KELVIN_MAX, 100, 0)
        return clip(p, 0, 100)

    def _send_data(self, data):
        try:
            r = requests.post(self.post_url, json=data, timeout=TIMEOUT)
        except (ConnectTimeout, ConnectionError):
            raise MatejLightException("Could not connect to lamp.")
        else:
            if r.text != "OK":
                raise MatejLightException("Command not successful. Data sent: {}".format(data))

    def set_brightness(self, percent):
        percent = clip(percent, 0, 100)
        data = {"brightness": percent-1}
        self.status["brightness"] = percent
        self._send_data(data)
        self.status["power"] = 1

    def set_temperature(self, kelvin):
        kelvin = clip(kelvin, KELVIN_MIN, KELVIN_MAX)
        percent_warm = map_val(kelvin, KELVIN_MIN, KELVIN_MAX, 100, 0)
        self.status["temperature"] = kelvin
        return self._set_temperature_percent(percent_warm)

    def _set_temperature_percent(self, percent_warm):
        data = {"whiteTemp": percent_warm}
        self._send_data(data)

    def set_aux_rgb(self, r, g, b):
        r = clip(r, 0, 100)
        g = clip(g, 0, 100)
        b = clip(b, 0, 100)
        self.status["aux_rgb"] = (r, g, b)
        data = {"R": r,
                "G": g,
                "B": b}
        self._send_data(data)

    def turn_off(self):
        self.status_before_off = self.status
        data = {"brightness": 0,
                "R": 0,
                "G": 0,
                "B": 0}
        self._send_data(data)
        self.status["power"] = 0

    def turn_on(self):
        self.status = self.status_before_off
        self.set_brightness(self.status["brightness"])
        self.set_aux_rgb(*self.status["aux_rgb"])
        self.status["power"] = 1

    def _get_data(self):
        try:
            r = requests.get(self.get_url, timeout=TIMEOUT)
        except (ConnectTimeout, ConnectionError):
            raise MatejLightException("Could not connect to lamp.")
        else:
            try:
                data = r.json()
            except json.decoder.JSONDecodeError:
                raise MatejLightException("Could not decode received JSON data. Received was: {}".format(r.text))
            else:
                return data

    def get_status(self):
        data = self._get_data()
        status = {"brightness": data["brightness"],
                  "temperature": self.percent_warm_2_kelvin(data["whiteTemp"]),
                  "aux_rgb": (data["R"], data["G"], data["B"]),
                  "power": self.status["power"]}  # TODO implement
        return status

    def update(self):
        self.status = self.get_status()

    def is_available(self):
        try:
            self.get_status()
        except:
            return False
        else:
            return True


if __name__ == '__main__':
    from time import sleep
    l = MatejLight("192.168.1.15")
    l.set_brightness(100)

    # print(l.status)
    # sleep(3)
    # l.turn_off()
    # print(l.status)
    # sleep(3)
    # l.set_brightness(50)
    # l.set_temperature(5000)
    l.update()
    print(l.status)




