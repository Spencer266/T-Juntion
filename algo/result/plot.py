from cProfile import label
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import matplotlib.pyplot as plt

from utils.calculation import get_average

def file_to_list(src):
    output = []

    with open(src, 'r') as f:
        for line in f:
            stripped_line = line.strip()
            output.append(float(stripped_line))

        f.close()

    return output

sac_rewards = file_to_list("./sac/sac_reward.txt")
nsac_rewards = file_to_list("./sac_noise/nsac_reward.txt")

max_episode = 4000

avg_sac_rewards = get_average(sac_rewards, max_episode)
avg_nsac_rewards = get_average(nsac_rewards, max_episode)

episodes = [i for i in range(max_episode)]

plt.figure(figsize=(10, 15))

## SAC
plt.plot(episodes, avg_sac_rewards, 'r', label='SAC')

## NSAC
plt.plot(episodes, avg_nsac_rewards, 'c', label='NSAC')

plt.title('Average reward')
plt.xlabel("Episode")
plt.ylabel("Average Reward")
plt.grid(True)
plt.legend()
plt.show()

