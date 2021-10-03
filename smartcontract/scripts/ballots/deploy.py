#!/usr/bin/python3
from brownie import Ballots, config, network
from scripts.helpful_scripts import (
    get_account,
    # get_contract,
)


def deploy_ballots():
    account = get_account()

    ballots = Ballots.deploy(
        {'from':account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"ballot-list deployed")
    return ballots


def main():
    deploy_ballots()
