import matplotlib
from sac import SACAgent
# from plotting.plot import PlotHelper
import matplotlib.pyplot as plt

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from gym_unity.envs import UnityToGymWrapper

channel = EngineConfigurationChannel()

unity_env = UnityEnvironment('../../New folder/Player Control.exe', side_channels=[channel], seed=42, worker_id=1)
channel.set_configuration_parameters(time_scale=6.0)

env = UnityToGymWrapper(unity_env, True)

gamma = 0.99
tau = 0.01
alpha = 0.2
a_lr = 3e-4
q_lr = 3e-4
p_lr = 3e-3
buffer_maxlen = 1000000

max_episode = 20

agent = SACAgent(env, gamma, tau, alpha, q_lr, p_lr, a_lr, buffer_maxlen)

def sac_train(env, agent, max_episode, max_step, batch_size):
  episode_rewards = []
  update_step = 0

  for episode in range(max_episode):
    state = env.reset()
    episode_reward = 0

    for step in range(max_step):
      action = agent.get_action(state)
      next_state, reward, done, _ = env.step(action)
      agent.replay_buffer.push(state, action, reward, next_state, done)
      episode_reward += reward

      if len(agent.replay_buffer) > batch_size:
        agent.update(batch_size)
        update_step += 1

      if done or step == max_step - 1:
        episode_rewards.append(episode_reward)
        break
      
      state = next_state
    if episode % 10 == 0:
      print("Episode " + str(episode) + ": " + str(episode_reward))

  return episode_rewards

episode_rewards = sac_train(env, agent, max_episode, 500, 64)

def plot_hundred(max_episode, episode_rewards):
    episodes = [i for i in range(max_episode) if i % 100 == 0]

    reward_per_hundred = [episode_rewards[i] for i in range(max_episode) if i % 100 == 0]

    plt.figure(figsize=(10, 15))
    plt.plot(episodes, reward_per_hundred)
    plt.title('Reward per 100 episodes')
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.show()

# PlotHelper.plot_hundred(max_episode, episode_rewards)
plot_hundred(max_episode, episode_rewards)