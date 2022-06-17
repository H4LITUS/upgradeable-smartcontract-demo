from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    network,
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
)


def deploy_and_create():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account}, publish_source=False)
    print(box.retrieve())

    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=False)

    # initializer = box.store, 3
    box_encoded_initializer_function = encode_function_data(box.store, 2)

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=False,
    )

    print(f"Proxy deployed to {proxy}......You can now upgrade to V2")

    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    print(proxy_box.retrieve({"from": account}))
    proxy_box.store(5, {"from": account})
    print(proxy_box.retrieve({"from": account}))

    box_v2 = BoxV2.deploy({"from": account}, publish_source=False)

    upgrade_tx = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_tx.wait(1)
    print("Proxy has been upgraded to BoxV2")

    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    tx = proxy_box.increment({"from": account})
    tx.wait(1)
    print(proxy_box.retrieve({"from": account}))


def main():
    deploy_and_create()
