import bolt11
from bolt11.types import Bolt11
from bolt11.models.signature import Signature

# verify_payload = {
#     "status": "OK",
#     "settled": False,
#     "preimage": None,
#     "pr": "lnbc1u1pnfc2utpp52pgctflumy77l7zcwyv8hcu37yq3ha9aleh8vqpgcalqduqtfs8shp5fwml5q5dckdwq4c2njau2jc9prswd0q43t5aauwv56zwdgw6h6pscqzzsxqyz5vqsp5897mqnprgwmchgdd4l2zx9u5szuvgrqkw73n7kaqr00pw73fgqls9qxpqysgq6ghjpqkav6qm9nt2vncv92muprv7h6zfxxcu29femukgrdud5hq3ljpf9hc7g7vajjgsysevf5cc5y3utanx2ud6lf35cagel7ugrucqpp0vfw"
# }

verify_payload = {
    "status": "OK",
    "settled": True,
    "preimage": "471fc48ab6e618cb7d05d544d75c320faa2ea9011e476a2c3d5680772fc69ce4",
    "pr": "lnbc1u1pnfmkukpp5y08x9r6wga58dz6m7mpsc6tug30tgflplq8k6c2u5paqfs6shacqhp5fwml5q5dckdwq4c2njau2jc9prswd0q43t5aauwv56zwdgw6h6pscqzzsxqyz5vqsp5pjnaqnezzwcur9j6v7da2pxxq6658knxk5rf9hcg67js2aqfavks9qxpqysgqysp9cfc9c78zesrq9jzmecjq9e7gre97x94px9f34lxu8f2w2x4kgy66t94tkwelk5pc3vg8kt5qgjntpzw53jwfxfx38r8pxh7dtwgqsmplas"
}




if __name__ == "__main__":
    pr = verify_payload['pr']
    invoice_date: Bolt11 = bolt11.decode(pr)

    # TODO: how can we validate a signature?
    # if invoice_date.validate():
    if invoice_date.signature.verify():
        print("✅ Invoice is valid")
    else:
        print("❌ Invoice is invalid")

    if not invoice_date.has_expired():
        print("✅ Invoice has not expired")
    else:
        print("❌ Invoice has expired")

    if invoice_date.is_mainnet():
        print("✅ Mainnet Invoice")
    else:
        print("❌ These coins are worthless!! Invoice")

    print(f"Currency: {invoice_date.currency}")
    print(f"Date: {invoice_date.data}")
    print(f"Tags: {invoice_date.tags}")
    print(f"Amount: {invoice_date.amount_msat}")

    # print(f"Signature: {invoice_date.signature}")

    # for key, value in invoice_date.items():
    #     print(key, value)

    # print(invoice_date)
