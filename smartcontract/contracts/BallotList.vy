# @version ^0.2.0

"""
@title a list of all held ballot
"""

### https://github.com/kpeluso/vyper-dynamic-array
### TODO: make dynamic
ballotList: address[100]
maximum: uint256


@external
def add_ballot(id: address):
    self.ballotList[self.maximum] = id
    self.maximum += 1

@view
@external
def get_ballots() -> address[100]:
    return self.ballotList
