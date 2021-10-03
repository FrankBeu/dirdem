# @version ^0.2.0

"""
@title a basic user - only attributes are name and gender
"""

struct User_obj:
    name: String[50]
    gender: int128

MALE: constant(int128) = 0
FEMALE: constant(int128) = 1
OTHER: constant(int128) = 2

user: User_obj


@external
def setUser(name: String[50], gender: String[10]):
    assert gender == "male" or gender == "female" or gender == "other", "gender must be 'male', 'female' or 'other'"
    _gender_code: int128 = OTHER
    if gender == "male":
        _gender_code = MALE
    elif gender == "female":
        _gender_code = FEMALE
    else:
        _gender_code = OTHER
    self.user = User_obj({name: name, gender: _gender_code})

@external
@view
def getUser() -> (String[50], String[10]):
    _gender: String[10] = "other"
    if self.user.gender == MALE:
        _gender = "male"
    elif self.user.gender == FEMALE:
        _gender = "female"
    else:
        _gender = "other"
    return self.user.name, _gender
