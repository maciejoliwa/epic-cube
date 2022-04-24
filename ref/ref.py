import typing as tp

class Reference:

    _value: tp.Any

    def __init__(self, value: tp.Any) -> None:
        self._value = value

    def get(self) -> tp.Any:
        return self._value

    def set(self, new_value: tp.Any) -> tp.Any:
        if type(new_value) == type(self._value):
            self._value = new_value
        else:
            print(f"{new_value} is not the same type as {self._value}")