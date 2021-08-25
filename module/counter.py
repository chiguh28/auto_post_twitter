class Counter():
    """カウンター
    """
    def __init__(self) -> None:
        self.count = 0

    def get_count(self) -> int:
        """カウント取得
        現在のカウントを渡す

        Returns:
            int: [description]
        """
        return self.count

    def count_up(self) -> None:
        self.count += 1

    def count_down(self) -> None:
        self.count -= 1

    def count_clear(self) -> None:
        self.count = 0

    def can_count_up(self, max):
        return self.count < max
