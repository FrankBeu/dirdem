#!/usr/bin/python3
from brownie import Ballot, config, network
from scripts.helpful_scripts import (
    get_account,
    # get_contract,
)


def deploy_ballot():
    account = get_account()

    ballot = Ballot.deploy(
        'test', 'Does it work?', 120,
        {'from':account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    # user = User.deploy 
        # {"from": account},
        # publish_source=config["networks"][network.show_active()].get("verify", False),
    # )
    print(f"ballot deployed")
    return ballot

    # eth_usd_price_feed_address = get_contract("eth_usd_price_feed").address
    # price_feed = PriceFeedConsumer.deploy(
    #     eth_usd_price_feed_address,
    #     {"from": account},
    #     publish_source=config["networks"][network.show_active()].get("verify", False),
    # )


def main():
    deploy_ballot()
