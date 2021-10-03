#!/usr/bin/python3
from brownie import BallotList, config, network
from scripts.helpful_scripts import (
    get_account,
    # get_contract,
)


def deploy_ballotList():
    account = get_account()

    ballotList = BallotList.deploy(
        {'from':account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"ballotList deployed:")
    print(f"Address:")
    print(ballotList.address)
    return ballotList


def main():
    deploy_ballotList()
