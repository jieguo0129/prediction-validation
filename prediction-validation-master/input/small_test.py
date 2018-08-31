from decimal import Decimal, ROUND_HALF_UP

class MovingAverageComputer:
    def __init__(self, window_size):
        self.window_size = window_size
        self.sum_list = [0] * window_size
        self.cnt_list = [0] * window_size
        self.index = -1
        self.sum = 0.0
        self.cnt = 0

    def GetAverage(self, cur_sum, cur_cnt):
        self.index = (self.index + 1) % self.window_size
        self.sum = self.sum - self.sum_list[self.index] + cur_sum
        self.cnt = self.cnt - self.cnt_list[self.index] + cur_cnt
        self.sum_list[self.index] = cur_sum
        self.cnt_list[self.index] = cur_cnt
        if self.cnt == 0:
            return 'NA'
        else:
            return (Decimal(self.sum) / self.cnt).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            # return round(Decimal(str(self.sum)) / self.cnt, 2)

def average_error(actual_fname, predicted_fname):
    total = 0
    cnt = 0
    actual = {}
    n1 = 0
    n2 = 0
    with open(actual_fname) as actual_file:
        for line in actual_file:
            n1 = n1 + 1
            tokens = line.split('|')
            k1 = tokens[0] + tokens[1]
            v1 = tokens[2].replace(".", "")
            actual[k1] = int(v1)
    with open(predicted_fname) as predicted_file:
        for line in predicted_file:
            n2 = n2 + 1
            tokens = line.split('|')
            k1 = tokens[0] + tokens[1]
            v1 = tokens[2].replace(".", "")
            if k1 in actual:
                total = total + abs(actual[k1] - int(v1))
                cnt = cnt + 1
                actual.pop(k1)
    # print Decimal(total / cnt).quantize(Decimal('.0001'), rounding=ROUND_HALF_UP)
    print (n1, n2)
    print len(actual)
    print total
    print cnt
    print 1.0 * (total / cnt) / 100


def main():
    average_error("actual.txt", "predicted.txt")

if __name__ == "__main__":
    main()


