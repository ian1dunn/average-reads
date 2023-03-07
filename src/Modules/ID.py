import random

from GlobalStuff import increment_str, INCREMENT_START_CHAR

DEFAULT_ID_LENGTH = 8  # Default Length of the id


class ID:
    """
    Generic class for an ID. I figured this would be good because we will have multiple classes with ID's
    """
    def __init__(self, last_value: str | None = None, value: str = None, length: int = DEFAULT_ID_LENGTH):
        """
        Create an ID. The value will be extended to the length
        :param last_value: incremented the last value to create a new ID. None returns the base id of the
        given length (If a value is not given)
        :param value: create an ID with the given value
        :param length: length of the ID or the default ID length
        :exception thrown if the value exceeds the length
        """
        if not value:
            value = increment_str(last_value) if last_value else INCREMENT_START_CHAR * length

        diff = len(value) - length
        if diff < 0:  # Extend the ID to match the desired length
            value = INCREMENT_START_CHAR * abs(diff) + value
        elif diff != 0:  # Uh oh
            raise Exception(f"The value {value} exceeds the length by {diff}.")

        self.value = value

    def __str__(self):
        return f"ID: {self.value}"
    def getRandom(self,top):
        return str(random.randint(0,top))


if __name__ == '__main__':
    last=""
    for i in range(14):
        id = ID("1%")
        last = id.value
        print(id)

