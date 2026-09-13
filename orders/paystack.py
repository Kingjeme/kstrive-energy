import requests

from django.conf import settings


PAYSTACK_INITIALIZE_URL = (
    "https://api.paystack.co/transaction/initialize"
)

PAYSTACK_VERIFY_URL = (
    "https://api.paystack.co/transaction/verify/"
)


def get_headers():
    secret_key = settings.PAYSTACK_SECRET_KEY

    if not secret_key:
        raise ValueError(
            "Paystack secret key is missing. Check your .env file."
        )

    return {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }


def initialize_transaction(order, callback_url):
    payload = {
        "email": order.email,
        "amount": int(order.total * 100),
        "currency": "NGN",
        "reference": order.order_number,
        "callback_url": callback_url,
        "metadata": {
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "phone": order.phone,
        },
    }

    try:
        response = requests.post(
            PAYSTACK_INITIALIZE_URL,
            json=payload,
            headers=get_headers(),
            timeout=30,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        raise ValueError(
            f"Could not connect to Paystack: {error}"
        )

    try:
        data = response.json()
    except ValueError:
        raise ValueError(
            "Paystack returned an invalid response."
        )

    if not data.get("status"):
        message = data.get(
            "message",
            "Paystack transaction initialization failed.",
        )

        raise ValueError(message)

    authorization_url = (
        data.get("data", {}).get("authorization_url")
    )

    if not authorization_url:
        raise ValueError(
            "Paystack did not return an authorization URL."
        )

    return {
        "authorization_url": authorization_url,
        "reference": data["data"].get("reference"),
    }


def verify_transaction(reference):
    try:
        response = requests.get(
            f"{PAYSTACK_VERIFY_URL}{reference}",
            headers=get_headers(),
            timeout=30,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        raise ValueError(
            f"Could not verify Paystack payment: {error}"
        )

    try:
        data = response.json()
    except ValueError:
        raise ValueError(
            "Paystack returned an invalid verification response."
        )

    if not data.get("status"):
        raise ValueError(
            data.get(
                "message",
                "Paystack payment verification failed.",
            )
        )

    return data["data"]