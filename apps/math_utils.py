from decimal import Decimal, ROUND_HALF_UP


def round_decimal(val, quantize=2):
    return Decimal(val.quantize(Decimal('.{}1'.format('0'*(quantize-1))), rounding=ROUND_HALF_UP))
