class FourDigitYearConverter:
    regex = "[0-9]{4}"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%04d' % value


class TwoDigitMonthConverter:
    regex = "(0?[1-9]|1[012])"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%02d' % value


class TwoDigitDayConverter:
    regex = "(0[1-9]|[12][0-9]|3[01])"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%02d' % value
