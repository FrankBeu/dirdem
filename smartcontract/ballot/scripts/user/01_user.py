#!/usr/bin/python3
from brownie import User, config, network
from scripts.helpful_scripts import (
    get_account,
    # get_contract,
)


def deploy_user():
    account = get_account()
    # eth_usd_price_feed_address = get_contract("eth_usd_price_feed").address
    # price_feed = PriceFeedConsumer.deploy(
    #     eth_usd_price_feed_address,
    #     {"from": account},
    #     publish_source=config["networks"][network.show_active()].get("verify", False),
    # )
    user = User.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    # print(f"User deployed {user.getUser()}")
    print(f"User deployed")
    return user


def main():
    deploy_user()
