import sys 
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from gym_unity.envs import UnityToGymWrapper
import numpy as np

from sac import SACAgent
from plotting.plot import plot_avg, plot_ten, plot_loss
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
critic_lr = 3e-4
actor_lr = 3e-4
delay_step = 2
buffer_maxlen = 1000000

max_episode = 7000
max_step = 2000

agent = SACAgent(obs_dim, action_dim, gamma, tau, alpha, critic_lr, actor_lr, a_lr, buffer_maxlen, delay_step)

def sac_train(max_episode, max_step, batch_size):
  episode_rewards = []
  max_reward = 0

  for episode in range(max_episode):
    episode_reward = 0
    state = env.reset()
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

  env.close()

  return episode_rewards

episode_rewards = sac_train(max_episode, max_step, 128)

q_loss = agent.log['critic_loss']
p_loss = agent.log['policy_loss']
entropy_loss = agent.log['entropy_loss']

writeListToFile(episode_rewards, '../result/sac/sac_reward.txt')
writeListToFile(q_loss, '../result/sac/sac_critic.txt')
writeListToFile(p_loss, '../result/sac/sac_actor.txt')
writeListToFile(entropy_loss, '../result/sac/sac_entropy.txt')

plot_ten(max_episode, episode_rewards, 'SAC')

plot_avg(max_episode, episode_rewards, 'SAC')

plot_loss(max_episode, q_loss, 'Critic loss', 'SAC')

plot_loss(max_episode, p_loss, 'Policy loss', 'SAC')

plot_loss(max_episode, entropy_loss, 'Entropy loss', 'SAC')
