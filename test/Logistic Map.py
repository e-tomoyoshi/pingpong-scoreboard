import time
import random

x = random.random()

r = 3.99 # カオスのパラメータ（3.59を超えると混沌が始まります）

try:
    while True:
        #　ロジスティック写像の公式
        x = r * x * (1 - x)

        pos = int(x * 70) + 5
        print(" " * pos + "*")

        #　ほんの少し待つと、滝のように流れる様子が見えます
        time.sleep(0.05)

except KeyboardInterrupt:
    print