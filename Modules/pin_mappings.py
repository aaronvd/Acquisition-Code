import numpy as np

element_number_header_1 = np.array([8, 9,
                                    24, 25,
                                    40, 41,
                                    56, 57,
                                    72, 73,
                                    7, 10,
                                    23, 26,
                                    39, 42,
                                    55, 58,
                                    71, 74,
                                    6, 11,
                                    22, 27,
                                    38, 43,
                                    54, 59,
                                    70, 75,
                                    5, 12,
                                    21, 28,
                                    37, 44,
                                    53, 60,
                                    69, 76,
                                    4, 13,
                                    20, 29,
                                    36, 45,
                                    52, 61,
                                    68, 77,
                                    3, 14,
                                    19, 30,
                                    35, 46,
                                    51, 62,
                                    67, 78,
                                    2, 15,
                                    18, 31,
                                    34, 47,
                                    50, 63,
                                    66, 79,
                                    1, 16,
                                    17, 32,
                                    33, 48,
                                    49, 64,
                                    65, 80,
                                    161])
element_number_header_1 = np.concatenate(
    (element_number_header_1, np.zeros(120 - element_number_header_1.size)))

element_number_header_1 = element_number_header_1.reshape((60, 2))
element_number_header_1 = np.flip(element_number_header_1, axis=1).reshape(-1)

element_number_header_2 = np.array([81, 96,
                                    97, 112,
                                    113, 128,
                                    129, 144,
                                    145, 160,
                                    82, 95,
                                    98, 111,
                                    114, 127,
                                    130, 143,
                                    146, 159,
                                    83, 94,
                                    99, 110,
                                    115, 126,
                                    131, 142,
                                    147, 158,
                                    84, 93,
                                    100, 109,
                                    116, 125,
                                    132, 141,
                                    148, 157,
                                    85, 92,
                                    101, 108,
                                    117, 124,
                                    133, 140,
                                    149, 156,
                                    86, 91,
                                    102, 107,
                                    118, 123,
                                    134, 139,
                                    150, 155,
                                    87, 90,
                                    103, 106,
                                    119, 122,
                                    135, 138,
                                    151, 154,
                                    88, 89,
                                    104, 105,
                                    120, 121,
                                    136, 137,
                                    152, 153])
element_number_header_2 = np.concatenate(
    (np.zeros(120 - element_number_header_2.size), element_number_header_2))
element_number_header_2 = np.flip(element_number_header_2.reshape((60, 2)), axis=1).reshape(-1)

element_number_headers = np.concatenate((element_number_header_1, element_number_header_2)) - 1 # element indices starting at 0

element_pin_index = np.argsort(element_number_headers)[element_number_headers.tolist().count(-1):]

def make_ts_quickturn(element_voltages):
    element_pin_index = element_pin_index[:-1]
    ts = []
    for i in range(element_voltages.shape[0]):
        t = np.zeros(240)
        for j in range(element_voltages.shape[1]):
            t[element_pin_index[j]] = element_voltages[i,j]
        ts.append(t)
    return ts