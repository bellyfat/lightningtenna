"""
A simple script to grab a new blocksat testnet invoice and pay it using C-Lightning
"""

import os
import time

from blocksat_api import blocksat
from hashlib import sha256
from lightning import LightningRpc
from termcolor import colored
from uuid import uuid4


home = os.path.expanduser("~")
l1 = LightningRpc(home + "/.lightning/lightning-rpc")


def get_blocksat_invoice():
    # msg = "Hello, from the mesh!"
    msg = uuid4().hex
    print("Sending a message via the Blockstream Satellite service:")
    print(f'"{msg}"')
    print(f"\nSHA256 message digest:")
    print(colored(sha256(msg.encode()).hexdigest(), "magenta"))
    invoice = blocksat.place(msg, 10000, blocksat.TESTNET_SATELLITE_API)
    if invoice.status_code == 200:
        print("\nGot lightning invoice!")
        inv = invoice.json()
        print(f"Amount (msatoshi): {inv['lightning_invoice']['msatoshi']}")
        print(f"Payment hash: {inv['lightning_invoice']['rhash']}")
        print(f"UUID: {inv['uuid']}")
        # print(f"Payment request:\n"
        #       f"{inv['lightning_invoice']['payreq']}\n")
        # print(f"Message digest:")
        # print(colored(f"{inv['lightning_invoice']['metadata']['sha256_message_digest']}\n", 'magenta'))
        return inv["lightning_invoice"]["payreq"], msg
    else:
        print(f"Couldn't get invoice:\n{invoice.reason}\n{invoice.text}")
        return False


def pay_by_route(timeout=500):
    # invoice = input("Enter your BOLT11 invoice:\n")
    invoice, message = get_blocksat_invoice()
    if invoice:
        decoded = l1.decodepay(invoice)
        print("Decoded payment request")
        input("Press any key to pay invoice via mesh proxy")
        # route = l1.getroute(decoded["payee"], decoded["msatoshi"], 0)["route"]
        route = [
            {
                "id": "032bced86b432c62e89e02e67d460e1765a14b9701b247f9614aa6ebc4f085151a",
                "channel": "1583101x187x1",
                "direction": 1,
                "msatoshi": 10001,
                "amount_msat": 10001,
                "delay": 15,
            },
            {
                "id": "039d2201586141a3fff708067aa270aa4f6a724227d5740254d4e34da262a79c2a",
                "channel": "1579538x76x1",
                "direction": 0,
                "msatoshi": 10000,
                "amount_msat": 10000,
                "delay": 9,
            },
        ]
        # print("Got a route")
        print("Sending HTLC via the mesh...")
        # print(f"lightning-cli sendpay {route} {decoded['payment_hash']}")
        l1.sendpay(route, decoded["payment_hash"])
        print("Sent to mesh successfully. Waiting for response...")
        time.sleep(2)
        print(f"lightning-cli waitsendpay {decoded['payment_hash']} {timeout}")
        result = l1.waitsendpay(decoded["payment_hash"], timeout)
        print(colored("\nComplete! Invoice payment accepted.\n", "green"))
        print(f"Message sent: {colored(message, 'magenta')}")
        print(
            f"Payment preimage:\n{colored(result['payment_preimage'], 'yellow', attrs=['bold'])}"
        )
        # print(f"msatoshi sent: {result['msatoshi_sent']}")
    else:
        return


pay_by_route()
