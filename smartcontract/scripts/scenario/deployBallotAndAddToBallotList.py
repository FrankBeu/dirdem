#!/usr/bin/python3
from brownie import BallotList, Ballot, config, network
from scripts.helpful_scripts import (
    get_account,
    # get_contract,
)

def deploy_ballot():
    account = get_account()

    ballot = Ballot.deploy(
        'test', 'does it work',120,
        {'from':account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"ballot deployed")
    return ballot

def add_to_ballotList():
    account = get_account()

    BallotList[-1].add_ballot(Ballot[-1].address)
    print(f"ballot addedd to list")
    print()
    print()


def main():
    deploy_ballot()
    add_to_ballotList()
