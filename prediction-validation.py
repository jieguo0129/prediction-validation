import sys


class MovingAverageComputer:
    """
    This class is for calculating the moving average with incoming data stream.
    Assuming the window size is k, incoming data contains the sum_i and cnt_i,
    the moving average refers to: (sum_(i-k+1) + ... + sum_i) / (num_(i-k+1) + ... + cnt_i)
    Performance:
        Time complexity: O(1)
        Space complexity: O(window_size)
    Internally it uses two circular arrays to store the list of sum
    and the list of cnt in one moving window respectively.
    """
    def __init__(self, window_size):
        """
        :param window_size: the size of the moving window
        """
        self.window_size = window_size
        self.sum_list = [0] * window_size
        self.cnt_list = [0] * window_size
        self.index = -1
        self.sum = 0.0
        self.cnt = 0

    def GetAverage(self, cur_sum, cur_cnt):
        """
        This function does three jobs:
        1/ Remove the data that falls out of the window.
        2/ Add the new data
        3/ Calculate the average of current window.
        :param cur_sum: the current sum
        :param cur_cnt: the current cnt
        :return: the average of the current window.
        """
        self.index = (self.index + 1) % self.window_size
        self.sum = self.sum - self.sum_list[self.index] + cur_sum
        self.cnt = self.cnt - self.cnt_list[self.index] + cur_cnt
        self.sum_list[self.index] = cur_sum
        self.cnt_list[self.index] = cur_cnt
        if self.cnt == 0:
            return 'NA'
        else:
            return "%.2f" % (self.sum / self.cnt)


def GetWindowSize(window_fname):
    """
    Get the window size from the file.
    :param window_fname: the name of the file that contains window size.
    :return: the window size if the data is valid, 0 otherwise.
    """
    with open(window_fname) as window_file:
        window = window_file.readline()
        # In case there are empty lines.
        while window is not None and window == '\n':
            window = window_file.readline()
        if window is not None:
            try:
                return int(window)
            except ValueError:
                # In case the number is not valid.
                return 0
    return 0

def ReadNextLine(file):
    """
    Read next meaningful line in the file.
    :param file: the file object
    :return: the token list of the next line if there is, otherwise return empty list.
    """
    line = file.readline()
    if not line:
        return []
    tokens = line.split('|')
    if tokens and len(tokens) == 3:
        return tokens
    else:
        return ReadNextLine(file)

def PeekNextLine(file):
    """
    Peek next meaningful line in the file. It will not move the cursor of the file.
    :param file: the file object
    :return: the token list of the next line if there is, otherwise return empty list.
    """
    pos = file.tell()
    line = ReadNextLine(file)
    file.seek(pos)
    return line

def ShouldReadNextLine(file, cur_time):
    """
    To judge whether the nextline of the file should be read. If the next meaningful line is for cur_time,
    it returns true, otherwise it returns false.
    :param file: the file object.
    :param cur_time: the day number.
    :return: Boolean to denote whether next line is for cur_time.
    """
    line = PeekNextLine(file)
    if line is not None and int(line[0]) == cur_time:
        return True
    return False

def WriteToFile(file, begin, end, value):
    """
    Write the result to the output file.
    :param file: the file object of the output file.
    :param begin: beginning day.
    :param end: ending day.
    :param value: the average value.
    """
    file.write(str(begin) + '|' + str(end) + '|' + str(value) + '\n')

def ComputeErrors(window_fname, actual_fname, predicted_fname, error_fname):
    """
    The core function for validating the prediction. This function is optimized in two manners:
    1/ use MovingAverageComputer to achieve O(1) time complexity for calculating moving average.
    2/ iteratively read the actual_stock file and predicted_stock file to minimize the space usage.
    Performance:
        Time Complexity: O(#(lines in both file))
        Space Complexity: O( max(#(lines in just one day)), O(window_size))
    :param window_fname: the path/name of the file that stores window size.
    :param actual_fname: the path/name of the file that stores actual stock price.
    :param predicted_fname: the path/name of the file that stores predicted stock price.
    :param error_fname: the path/name of the file that stores the average errors(result).
    """
    win = GetWindowSize(window_fname)
    # if the number is not valid.
    if win <= 0:
        return

    average_computer = MovingAverageComputer(win)
    with open(actual_fname) as actual_file, open(predicted_fname) as predicted_file, \
            open(error_fname, "w") as output_file:
        try:
            peek_tokens = PeekNextLine(actual_file)
            if not peek_tokens:
                return
            # Get the first time in case it is not starting at 1.
            start_time = int(peek_tokens[0])
            cur_time = start_time
            while PeekNextLine(actual_file):
                cur_cnt = 0
                cur_sum = 0
                stock_price_map = {}
                # Calculate the error in one single time.
                while ShouldReadNextLine(actual_file, cur_time):
                    actual_stock_tokens = ReadNextLine(actual_file)
                    stock_name = actual_stock_tokens[1]
                    actual_stock_price = float(actual_stock_tokens[2])
                    stock_price_map[stock_name] = actual_stock_price
                while ShouldReadNextLine(predicted_file, cur_time):
                    predicted_stock_tokens = ReadNextLine(predicted_file)
                    stock_name = predicted_stock_tokens[1]
                    predicted_stock_price = float(predicted_stock_tokens[2])
                    if stock_name in stock_price_map:
                        delta = abs(stock_price_map.pop(stock_name, 0) - predicted_stock_price)
                        cur_sum = cur_sum + delta
                        cur_cnt = cur_cnt + 1
                average_error = average_computer.GetAverage(cur_sum, cur_cnt)
                # We only write to the output file when the collected data length reaches window size.
                if cur_time - win + 1 >= start_time:
                    WriteToFile(output_file, cur_time - win + 1, cur_time, average_error)
                cur_time = cur_time + 1
        except ValueError:
            # In case the input file has invalid number.
            print "There are invalid inputs"

def main():
    if len(sys.argv) != 5:
        print "Please verify that you input four file paths/names"
    ComputeErrors(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])


if __name__ == "__main__":
    main()


