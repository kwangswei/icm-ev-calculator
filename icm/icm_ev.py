from enum import Enum, auto
from pydantic import BaseModel


class HandResult(Enum):
    WIN = auto()
    TIE = auto()
    LOSE = auto()
    FOLD = auto()


class ICMEquityCalculator(BaseModel):
    stacks: list[float]
    prizes: list[float]

    def get(self) -> list[float]:
        self.prizes.sort(reverse=True)
        self.prizes[: len(self.stacks)]

        seen: list[bool] = [bool(e == 0) for i, e in enumerate(self.stacks)]
        non_zero_cnt = sum(n > 0 for n in self.stacks)

        equities = self._recursive_icm_equity(seen, sum(self.stacks), 0, 1.0)
        index = 0
        for i, stack in enumerate(self.stacks):
            if stack != 0:
                continue
            equities[i] = self.prizes[non_zero_cnt + index]
            index += 1

        return equities

    def _recursive_icm_equity(
        self,
        seen: list[bool],
        remain_stack: int,
        place: int,
        chance: float,
    ) -> list[float]:
        equities = [0.0] * len(self.stacks)
        if place >= len(self.prizes):
            return equities

        for i in range(len(self.stacks)):
            if seen[i] == True:
                continue

            stack = self.stacks[i]
            prize = self.prizes[place]
            p = float(stack) / float(remain_stack)
            equity = p * float(prize)
            equities[i] += chance * equity

            seen[i] = True
            eq = self._recursive_icm_equity(
                seen, remain_stack - stack, place + 1, chance * p
            )
            equities = [sum(x) for x in zip(equities, eq)]
            seen[i] = False

        return equities


class ICMEVCalculator(BaseModel):
    p_win: float
    p_tie: float
    p_lose: float
    stacks: list[float]
    prizes: list[float]
    hero: int
    villain: int

    def get(self) -> tuple[float, float]:
        ev_win = self._get_icm_ev(HandResult.WIN)
        ev_tie = self._get_icm_ev(HandResult.TIE)
        ev_lose = self._get_icm_ev(HandResult.LOSE)
        ev_fold = self._get_icm_ev(HandResult.FOLD)
        return (
            ev_win, ev_tie, ev_lose,
            self.p_win * ev_win
            + self.p_tie * ev_tie
            + self.p_lose * ev_lose,
            ev_fold,
        )

    def _get_icm_ev(self, kind: HandResult) -> float:
        pod_size = min(self.stacks[self.hero], self.stacks[self.villain])
        new_stack = self.stacks[:]

        match kind:
            case HandResult.WIN:
                new_stack[self.hero] += pod_size
                new_stack[self.villain] -= pod_size
            case HandResult.TIE:
                pass
            case HandResult.LOSE:
                new_stack[self.hero] -= pod_size
                new_stack[self.villain] += pod_size
            case HandResult.FOLD:
                pass

        equity_calculator = ICMEquityCalculator(stacks=new_stack, prizes=self.prizes[:])
        equities = equity_calculator.get()
        return equities[self.hero]


def main():
    stacks = [20, 10, 9, 2, 20]
    prizes = [125, 65, 40, 22, 10]

    equity_calculator = ICMEquityCalculator(stacks=stacks[:], prizes=prizes[:])
    print(f"{equity_calculator.get()}")

    ev_calc = ICMEVCalculator(
        p_win=0.454,
        p_tie=0.005,
        p_lose=0.541,
        stacks=stacks[:],
        prizes=prizes[:],
        hero=2,
        villain=1,
    )

    print(f"{ev_calc.get()}")

    ev_calc = ICMEVCalculator(
        p_win=0.588,
        p_tie=0.065,
        p_lose=0.347,
        stacks=stacks[:],
        prizes=prizes[:],
        hero=2,
        villain=1,
    )

    print(f"{ev_calc.get()}")


if __name__ == "__main__":
    main()
