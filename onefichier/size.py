from __future__ import print_function
from pydebugger.debug import debug

import bitmath

def convert(size, stype="mb"):
    stype = str(stype).strip().lower()
    debug(size = size)
    debug(stype = stype)
    size = float(size)

    if stype == 'mb':
        size = bitmath.Mb(size)
    elif stype == 'gb':
        size = bitmath.Gb(size)
    elif stype == 'tb':
        size = bitmath.Tb(size)
    elif stype == 'kb':
        size = bitmath.Kib(size)
    debug(size = size)

    #  print("sizeof_fmt 1=", sizeof_fmt(size))
    #  print("sizeof_fmt 2=", sizeof_fmt2(size))
    #  print("sizeof_fmt 3=", sizeof_fmt3(size))
    #  print("sizeof_fmt 4=", sizeof_fmt(size))
    #  print("human_size =", human_size(size))
    #  print("human_readable_bytes =", human_readable_bytes(size))
    #  print("get_human_readable_size =", get_human_readable_size(size))
    return size.Bit

def total(bit):
    return bitmath.Bit(bit).Gb


def sizeof_fmt(num):
    for x in [' bytes', ' KB', ' MB', ' GB', ' TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def sizeof_fmt2(num):
    """
        for actual with minus size
    """
    for x in [' bytes', ' KB', ' MB', ' GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, ' TB')


def sizeof_fmt3(num):
    from math import log
    unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'],
                    [0, 0, 1, 2, 2, 2])

    """Human friendly file size"""
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'

def sizeof_fmt4(num):
    """Human friendly file size"""
    from math import log
    if num > 1:
        exponent = int(log(num, 1024))
        quotient = num / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'

#drive = r'D:'
# print 'TotalSize of %s = %d GB' % (drive, TotalSize(drive))
# print 'FreeSpace on %s = %d GB' % (drive, FreeSpace(drive))


def human_size(size_bytes):
    """
    format a size in bytes into a 'human' file size, e.g. bytes, KB, MB, GB, TB, PB
    Note that bytes/KB will be reported in whole numbers but MB and above will have greater precision
    e.g. 1 byte, 43 bytes, 443 KB, 4.3 MB, 4.43 GB, etc
    """
    if size_bytes == 1:
        # because I really hate unnecessary plurals
        return "1 byte"

    suffixes_table = [('bytes', 0), ('KB', 0), ('MB', 1),
                      ('GB', 2), ('TB', 2), ('PB', 2)]

    num = float(size_bytes)
    for suffix, precision in suffixes_table:
        if num < 1024.0:
            break
        num /= 1024.0
        if precision == 0:
            formatted_size = "%d" % num
        else:
            formatted_size = str(round(num, ndigits=precision))

        return "%s %s" % (formatted_size, suffix)


def human_readable_data_quantity(quantity, multiple=1024):
    if quantity == 0:
        quantity = +0
    SUFFIXES = ["B"] + [i + {1000: "B", 1024: "iB"}[multiple]
                        for i in "KMGTPEZY"]
    for suffix in SUFFIXES:
        if quantity < multiple or suffix == SUFFIXES[-1]:
            if suffix == SUFFIXES[0]:
                return "%d%s" % (quantity, suffix)
            else:
                return "%.1f%s" % (quantity, suffix)
        else:
            quantity /= multiple


def human_readable_bytes(x):
    # hybrid of http://stackoverflow.com/a/10171475/2595465
    #      with http://stackoverflow.com/a/5414105/2595465
    from math import log
    if x == 0:
        return '0'
    magnitude = int(log(abs(x), 10.24))
    if magnitude > 16:
        format_str = '%iP'
        denominator_mag = 15
    else:
        float_fmt = '%2.1f' if magnitude % 3 == 1 else '%1.2f'
        illion = (magnitude + 1) // 3
        format_str = float_fmt + ['', ' Kb',
                                  ' Mb', ' Gb', ' Tb', ' Pb'][illion]
    # return (format_str % (x * 1.0 / (1024 ** illion))).lstrip('0')
    return (format_str % (x * 1.0 / (1024 ** illion)))


def get_human_readable_size(num):
    exp_str = [(0, 'B'), (10, 'KB'), (20, 'MB'), (30, 'GB'), (40, 'TB'), (50, 'PB'), ]
    i = 0
    while i + 1 < len(exp_str) and num >= (2 ** exp_str[i + 1][0]):
        i += 1
        rounded_val = round(float(num) / 2 ** exp_str[i][0], 2)
        return '%s %s' % (int(rounded_val), exp_str[i][1])