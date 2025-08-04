#calculate the sum of digits in number 12345
number = 12345
digit_sum= sum(int(digit) for digit in str(number))
print(digit_sum)