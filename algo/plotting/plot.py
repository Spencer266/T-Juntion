import matplotlib.pyplot as plt

def plot_ten(max_episode, episode_rewards, algo_name):
    episodes = [i for i in range(max_episode) if i % 10 == 0]

    reward_per_ten = [episode_rewards[i] for i in range(max_episode) if i % 10 == 0]

    plt.figure(figsize=(10, 15))
    plt.plot(episodes, reward_per_ten)
    plt.title('Reward per 10 episodes using ' + algo_name)
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.grid(True)
    plt.show()

def plot_loss(max_episode, loss, name, algo_name):
    episodes = [i for i in range(max_episode) if i % 10 == 0]

    loss_to_plot = [loss[i] for i in range(max_episode) if i % 10 == 0]

    plt.figure(figsize=(10, 15))
    plt.plot(episodes, loss_to_plot)
    plt.title(name + " using " + algo_name)
    plt.xlabel("Episode")
    plt.ylabel("Loss")
    plt.grid(True)
    plt.show()

def plot_avg(max_episode, episode_rewards, env_name):
    episodes = [i for i in range(max_episode)]

    average_rewards = [0.0 for i in range(max_episode)]

    for i in range(max_episode):
      average_rewards[i] = sum(episode_rewards[0:i+1]) / (i+1)

    plt.figure(figsize=(10, 15))
    plt.plot(episodes, average_rewards)
    plt.title('Average reward plot with ' + env_name)
    plt.xlabel("Episode")
    plt.ylabel("Average Reward")
    plt.grid(True)
    plt.show()

