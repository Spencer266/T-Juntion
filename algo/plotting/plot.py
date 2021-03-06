import matplotlib.pyplot as plt

class PlotHelper:


    def plot_hundred(self, max_episode, episode_rewards):
        episodes = [i for i in range(max_episode) if i % 100 == 0]

        reward_per_hundred = [episode_rewards[i] for i in range(max_episode) if i % 100 == 0]

        plt.figure(figsize=(10, 15))
        plt.plot(episodes, reward_per_hundred)
        plt.title('Reward per 100 episodes')
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.show()