import os


def solve_filepath(path):
    if not path:
        return ''

    if path[0] == '/':
        return path
    elif os.path.exists(path):
        return path
    else:
        mydir = os.path.dirname(os.path.realpath(__file__))
        return mydir + '/' + path


def convert_freq_to_number(text: str, default_unit="THZ"):
    text = text.upper()
    figure = 0
    multiplier = 1

    for i in range(2):
        if text.endswith("THZ"):
            figure = float(text[:-3].strip())
            multiplier = 1e12
        elif text.endswith("GHZ"):
            figure = float(text[:-3].strip())
            multiplier = 1e9
        elif text.endswith("MHZ"):
            figure = float(text[:-3].strip())
            multiplier = 1e6
        elif text.endswith("KHZ"):
            figure = float(text[:-3].strip())
            multiplier = 1e3
        elif text.endswith("HZ"):
            figure = float(text[:-2].strip())
            multiplier = 1
        else:
            text += default_unit

    return figure * multiplier


def convert_freq_for_display(freq):
    # max precision is 0.1 MHz

    if freq >= 1e12:
        return f"{freq/1e12:.6f} THz"
    elif freq >= 1e9:
        return f"{freq/1e9:.3f} GHz"
    elif freq >= 1e6:
        return f"{freq/1e6:.1f} MHz"
    else:
        return "<1 MHz"


def convert_freq_for_forms(freq):
    # max precision is 0.1 MHz

    if freq >= 1e12:
        return f"{freq/1e12:.6f} THz"
    elif freq >= 1e9:
        return f"{freq/1e9:.3f} GHz"
    elif freq >= 1e6:
        return f"{freq/1e6:.1f} MHz"
    else:
        return "0"
