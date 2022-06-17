from re import A
from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    exceptions,
)
import pytest


def test_proxy_upgrades():
    account = get_account()
    box = Box.deploy({"from": account})

    proxy_admin = ProxyAdmin.deploy({"from": account})
    box_encoded_function_data = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_function_data,
        {"from": account, "gas_limit": 1000000},
    )

    box_v2 = BoxV2.deploy({"from": account})
    proxy_box = Contract.from_abi("BoxV2", proxy, BoxV2.abi)

    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box.increment({"from": account})

    upgrade(account, proxy, box_v2.address, proxy_admin_contract=proxy_admin)

    assert proxy_box.retrieve({"from": account}) == 0
    tx = proxy_box.increment({"from": account})
    tx.wait(1)
    assert proxy_box.retrieve({"from": account}) == 1
