from factor.BaseFactor import ArrayManager as ArrayManager_
import talib
import numpy as np
from typing import Union


class ArrayManager(ArrayManager_):
    def __init__(self, size):
        super().__init__(size=size)

    def get_public_factor(self):
        """
        返回在因子分析阶段所用到的公共因子（BaseFactor.py内的）
        """
        public_factor_ls = ["rsi", "roc", "mom"]
        return public_factor_ls

    def sma(self, n: int, array: bool = False) -> Union[float, np.ndarray]:
        """
        Simple moving average.
        """
        result: np.ndarray = talib.SMA(self.close, n)
        if array:
            return result
        return result[-1]




