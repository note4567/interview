# クローリングしたアイテムを数えるクラス
from typing import Callable


class CountItem:
    def __init__(self) -> None:
        pass

    def counter_item(self) -> Callable[..., int]:
        count = 0

        def increase(self=None) -> int:
            nonlocal count
            count += 1
            return count

        return increase
