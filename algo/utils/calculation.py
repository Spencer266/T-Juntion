def get_average(input_list, length):
    res = [0.0 for i in range(length)]

    for i in range(length):
      res[i] = sum(input_list[0:i]) / (i+1)

    return res