import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from gym_unity.envs import UnityToGymWrapper
import numpy as np

from sac_noise import SAC_NoiseAgent
from plotting.plot import plot_ten, plot_avg, plot_loss
from utils.write import writeListToFile

channel = EngineConfigurationChannel()

unity_env = UnityEnvironment('../../New folder (2)/Player Control.exe', side_channels=[channel], seed=42, worker_id=1)
channel.set_configuration_parameters(time_scale=3.0)

env = UnityToGymWrapper(unity_env, uint8_visual=True)

obs_dim = env.observation_space.shape[0]
action_dim = env.action_space.n

gamma = 0.99
tau = 0.01
alpha = 0.2
a_lr = 1e-4
q_lr = 3e-4
p_lr = 3e-4
noise_std = 0.2
noise_bound = 0.5
delay_step = 2
buffer_maxlen = 1000000

max_episode = 7000
max_step = 2000

agent = SAC_NoiseAgent(obs_dim, action_dim, gamma, tau, alpha, q_lr, p_lr, a_lr, noise_std, noise_bound, buffer_maxlen)

def sac_noise_train(max_episode, max_step, batch_size):
  episode_rewards = []
  max_reward = 0

  for episode in range(max_episode):
    state = env.reset()
    episode_reward = 0

    for step in range(max_step):
      action = agent.get_action(state)
      next_state, reward, done, _ = env.step(np.argmax(action))
      agent.replay_buffer.push(state, action, reward, next_state, done)
      episode_reward += reward

      if len(agent.replay_buffer) > batch_size:
        agent.update(batch_size)

      if done or step == max_step - 1:
        episode_rewards.append(episode_reward)
        break
      
      state = next_state

    if episode_reward > max_reward:
      agent.save_checkpoint()
      max_reward = episode_reward

    if episode % 10 == 0:
      print("Episode " + str(episode) + ": " + str(episode_reward))

  return episode_rewards

episode_rewards = sac_noise_train(max_episode, max_step, 128)

q_loss = agent.log['critic_loss']
p_loss = agent.log['policy_loss']
entropy_loss = agent.log['entropy_loss']

writeListToFile(episode_rewards, '../result/sac_noise/nsac_reward.txt')
writeListToFile(q_loss, '../result/sac_noise/nsac_critic.txt')
writeListToFile(p_loss, '../result/sac_noise/nsac_actor.txt')
writeListToFile(entropy_loss, '../result/sac_noise/nsac_entropy.txt')

plot_ten(max_episode, episode_rewards, 'Noisy SAC')
plot_avg(max_episode, episode_rewards, 'Noisy SAC')
plot_loss(max_episode, q_loss, 'Critic loss', 'Noisy SAC')
plot_loss(max_episode, p_loss, 'Policy loss', 'Noisy SAC')
plot_loss(max_episode, entropy_loss, 'Entropy loss', 'Noisy SAC')