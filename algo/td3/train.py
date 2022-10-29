import sys 
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from gym_unity.envs import UnityToGymWrapper

from td3 import TD3Agent
from plotting.plot import plot_avg, plot_ten, plot_loss
from utils.write import writeListToFile

channel = EngineConfigurationChannel()

unity_env = UnityEnvironment('../../New folder (2)/Player Control.exe', side_channels=[channel], seed=42, worker_id=1)
channel.set_configuration_parameters(time_scale=3.0)

env = UnityToGymWrapper(unity_env, uint8_visual=True, flatten_branched=True)

state_dim = env.observation_space.shape[0]
action_dim = env.action_space.n

gamma = 0.9
tau = 0.01
critic_lr = 1e-4
actor_lr = 1e-4
noise_std = 0.2
noise_bound = 0.5
delay_step = 2
buffer_maxlen = 1000000
max_step = 2000

max_episode = 7000

agent = TD3Agent(state_dim, action_dim, gamma, tau, buffer_maxlen, delay_step, noise_std, noise_bound, critic_lr, actor_lr)

def td3_train(max_episode, max_step, batch_size):
  episode_rewards = []

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

    agent.save_checkpoint()

    if episode % 10 == 0:
      print("Episode " + str(episode) + ": " + str(episode_reward))

  env.close()

  return episode_rewards

episode_rewards = td3_train(max_episode, max_step, 128)

q_loss = agent.log['critic_loss']
p_loss = agent.log['policy_loss']

writeListToFile(episode_rewards, '../result/td3/td3_reward.txt')
writeListToFile(q_loss, '../result/td3/td3_critic.txt')
writeListToFile(p_loss, '../result/td3/td3_actor.txt')

plot_ten(max_episode, episode_rewards)

plot_avg(max_episode, episode_rewards, 10, 'TD3')

plot_loss(max_episode, q_loss, 'Critic loss', 'TD3')

plot_loss(max_episode, p_loss, 'Policy loss', 'TD3')

