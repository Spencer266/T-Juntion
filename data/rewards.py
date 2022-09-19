import matplotlib.pyplot as plt
import csv

episodes = []
rewards = []

with open('rewards.csv', 'r') as rew_csv:
    lines = csv.reader(rew_csv, delimiter=',')
    next(lines)
    for line in lines:
        episodes.append(int(line[0]))
        rewards.append(float(line[1]))

plt.figure(figsize=(10, 15))
plt.plot(episodes, rewards)
plt.title('Fixed time environment')
plt.xlabel("Episode")
plt.ylabel("Reward")
plt.grid(True)
plt.show()