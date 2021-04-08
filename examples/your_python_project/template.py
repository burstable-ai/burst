import numpy as np
import matplotlib.pyplot as plt

x = np.arange(10)
y = x**2 

for i in range(len(x)):
    print('{} * {} = {}'.format(x[i], x[i], y[i]))

plt.scatter(x, y)
plt.savefig('example.png')

