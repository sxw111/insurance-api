from decimal import Decimal


def calculate_insurance(declared_value: Decimal, tariff_rate: Decimal):
    return declared_value * tariff_rate
