from datetime import datetime, timedelta
from enum import IntEnum

REFERENCE_TIME_0 = datetime(year=1900, month=1, day=1)
REFERENCE_TIME_1 = datetime(year=2036, month=2, day=7,
                                       hour=6, minute=28, second=16)


class LeapIndicator(IntEnum):
    NO_WARNING = 0
    SIXTY_ONE_IN_LAST_MINUTE = 1
    FIFTY_NINE_IN_LAST_MINUTE = 2
    ALARM = 3


class Mode(IntEnum):
    RESERVED = 0
    SYMMETRIC_ACTIVE = 1
    SYMMETRIC_PASSIVE = 2
    CLIENT = 3
    SERVER = 4
    BROADCAST = 5
    NTP_CONTROL_RESERVED = 6
    PRIVATE_RESERVED = 7


class StnpMessage:
    def __init__(self,
                 li=LeapIndicator.NO_WARNING,
                 version=4,
                 mode=Mode.SERVER,
                 stratum=1,
                 poll=4,
                 precision=0,
                 delay=0,
                 dispersion=0,
                 ref_id=b"LOCL",
                 request=None):
        self._request = request
        self._li = li
        self._version = version
        self._mode = mode
        self._stratum = stratum
        self._poll = poll
        self._precision = precision
        self._delay = delay
        self._dispersion = dispersion
        self._ref_id = ref_id
        self._curr_time = StnpMessage.read_time_differance() + datetime.utcnow()

    @staticmethod
    def read_time_differance():
        try:
            file = open("config")
            return timedelta(seconds=int(file.readline()))
        except Exception:
            return timedelta(seconds=0)

    @staticmethod
    def make_response(request):
        try:
            StnpMessage.check_correctness(request)
            response = StnpMessage(request=request).to_bytes()
        except Exception:
            return None
        return response

    def to_bytes(self):
        bytes_ = bytearray(48)
        bytes_[0] = ((self._li & 0b11) << 6) | \
                     ((self._version & 0b111) << 3) | \
                     (self._mode & 0b111)
        bytes_[1] = self._stratum.to_bytes(1, "big")[0]
        bytes_[2] = self._poll.to_bytes(1, "big")[0]
        bytes_[3] = self._precision.to_bytes(1, "big", signed=True)[0]
        bytes_[4:12] = bytearray([0x0] * 8)
        bytes_[12:16] = self._ref_id
        bytes_[16:24] = StnpMessage.time_to_bytes(self._curr_time)
        bytes_[24:32] = self._request[40:48]
        bytes_[32:40] = StnpMessage.time_to_bytes(self._curr_time)
        bytes_[40:48] = StnpMessage.time_to_bytes(self._curr_time)
        return bytes_

    @staticmethod
    def time_to_bytes(time):
        if time < REFERENCE_TIME_0 or time >= REFERENCE_TIME_1:
            raise ValueError

        if time >= REFERENCE_TIME_1:
            reference_time = REFERENCE_TIME_1
        else:
            reference_time = REFERENCE_TIME_0

        delta_seconds = (time - reference_time).total_seconds()

        seconds_fraction = int((delta_seconds - int(delta_seconds)) * (2 ** 32))

        return (int(delta_seconds).to_bytes(4, 'big') +
                seconds_fraction.to_bytes(4, 'big'))

    @staticmethod
    def check_correctness(bytes_):
        possible_length = set([48, 52, 64, 68])
        if len(bytes_) not in possible_length:
            raise ValueError
        leap_indicator = LeapIndicator((bytes_[0] & 0b11000000) >> 6)
        mode = Mode(bytes_[0] & 0b00000111)
        if mode != Mode.CLIENT:
            raise ValueError
