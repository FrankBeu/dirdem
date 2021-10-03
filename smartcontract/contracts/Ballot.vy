# @version ^0.2.0

"""
@title a ballot for arbitrary boolean questions
"""

### contract storage variables
title:          public(String[50])
question:       public(String[100])
deadline:       public(uint256)
timelimit:      public(uint256)
resultPositive: public(int128)
resultNegative: public(int128)
# ended: bool


### Information about voters
struct Voter:
    ### TODO: currently the EOA is not used otherwise only people having a wallet would be able to vote
    # id: address
    id: String[30]
    ### if true, that person already voted 
    voted: bool


# voters: public(HashMap[address, Voter])
voters: public(HashMap[String[30], Voter])

### setup global variables
@external
def __init__(_title: String[50], _question: String[100], _timelimit: uint256):
    self.title     = _title
    self.question  = _question
    self.timelimit = _timelimit
    self.deadline  = block.timestamp + _timelimit


### needs XOR:
###            https://github.com/ethereum-alarm-clock/ethereum-alarm-clock
###            has to be activate lazily on results - currently @view is needed to display results-cannot call state-modifying func
# @internal
# def try_to_set_ballot_ended_flag():
#     if block.timestamp > self.deadline:
#        self.ended = True


@external
def vote(id: String[30], vote: bool):
# def vote(name: address, vote: bool):
    ### Throws if the ballot is closed
    assert block.timestamp < self.deadline, "ballot already closed"

    ### Throws if the voter has already voted.
    assert not self.voters[id].voted, "cannot vote multiple times"

    if vote:
        self.resultPositive += 1 
    else:
        self.resultNegative += 1 

    self.voters[id].voted = True

# @view
# @external
# def results() -> (bool, int128, int128):
#     if not self.ended:
#        self.try_to_set_ballot_ended_flag()
#     return self.ended, self.resultPositive, self.resultNegative

@view
@external
def state() -> (address, String[50], String[100], uint256, uint256, int128, int128):
    return self, self.title, self.question, self.deadline, self.timelimit, self.resultPositive, self.resultNegative
