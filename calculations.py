from math import pow
from math import log10
from inspect import currentframe
debug = True


def debug_print(str):
    cf = currentframe()
    if debug:
        print(str, "Moduel:" + __name__, "Line:" + str(cf.f_back.f_lineno))
#  calculating, body fat, progress using different methods.


def seven_skin_fold(age, chest, belly, thigh, tricep, subscapula, hip, midaxillary):
    s = float(chest) + float(belly) + float(thigh) + float(tricep) + float(subscapula) + float(hip) + float(midaxillary)

    body_fat_procent = 495 / (1.112 - (0.00043499 * s) + (0.00000055 * s * s) - (0.00028826 * int(age))) - 450
    return round(body_fat_procent, 2)


def culate_body_fat_tape(gender, waist, neck, height, hip, metric=True):
    if metric:  # if using metric, convert to inches
        debug_print('converting to inches')
        waist = waist * 0.393700787
        neck = neck * 0.393700787
        height = height * 0.393700787
        hip = hip * 0.393700787

    if gender == 'female':
        debug_print('calculating bodyfat for female')
        body_fat = 163.205 * log10(waist + hip - neck) - 97.684 * log10(height) - 78.387

    elif gender == 'male':
        debug_print('calculating bodyfat for male')
        body_fat = 86.010 * log10(waist - neck) - 70.041 * log10(height)+36.76

    return round(body_fat, 2)


def culate_bmi(height, weight):
    bmi = float(weight) / pow((float(height) / 100), 2)
    return round(bmi, 2)


def culate_possible_stats(height, weight):

    if height and weight:
        bmi = culate_bmi(height, weight)
        return bmi

