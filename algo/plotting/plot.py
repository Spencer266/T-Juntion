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

def plot_avg(max_episode, episode_rewards, step, algo_name):
    avgs = []
    avg_reward = 0
    for i in range(max_episode):
        avg_reward += episode_rewards[i]

        if i % step == 0:
            avgs.append(avg_reward // step)
            avg_reward = 0

    scale_ep = max_episode // step
    plot_step = [i for i in range(scale_ep)]

    plt.figure(figsize=(10, 15))
    plt.plot(plot_step, avgs)
    plt.title('Average Reward using ' + algo_name)
    plt.xlabel("Episode")
    plt.ylabel("Avg Reward")
    plt.grid(True)
    plt.show()

