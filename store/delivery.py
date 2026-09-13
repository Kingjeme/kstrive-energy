from decimal import Decimal


DELIVERY_RATES = {
    "Delta": Decimal("8000"),
    "Edo": Decimal("8000"),

    "Rivers": Decimal("10000"),
    "Bayelsa": Decimal("10000"),
    "Akwa Ibom": Decimal("10000"),

    "Anambra": Decimal("9000"),
    "Imo": Decimal("9000"),
    "Abia": Decimal("9000"),
    "Enugu": Decimal("9000"),

    "Lagos": Decimal("8000"),
    "Ogun": Decimal("8000"),

    "Abuja": Decimal("12000"),
    "FCT": Decimal("12000"),

    "Adamawa": Decimal("12000"),
    "Bauchi": Decimal("12000"),
    "Benue": Decimal("12000"),
    "Borno": Decimal("12000"),
    "Cross River": Decimal("12000"),
    "Ebonyi": Decimal("12000"),
    "Ekiti": Decimal("12000"),
    "Gombe": Decimal("12000"),
    "Jigawa": Decimal("12000"),
    "Kaduna": Decimal("12000"),
    "Kano": Decimal("12000"),
    "Katsina": Decimal("12000"),
    "Kebbi": Decimal("12000"),
    "Kogi": Decimal("12000"),
    "Kwara": Decimal("12000"),
    "Nasarawa": Decimal("12000"),
    "Niger": Decimal("12000"),
    "Ondo": Decimal("12000"),
    "Osun": Decimal("12000"),
    "Oyo": Decimal("12000"),
    "Plateau": Decimal("12000"),
    "Sokoto": Decimal("12000"),
    "Taraba": Decimal("12000"),
    "Yobe": Decimal("12000"),
    "Zamfara": Decimal("12000"),
}


def get_delivery_fee(state):
    """
    Return the delivery fee for a Nigerian state.
    Unknown states use the standard ₦12,000 rate.
    """
    return DELIVERY_RATES.get(state, Decimal("12000"))