import sys 
import os
import numpy as np

from discrete_sac import SACAgent
from utils import ReplayBuffer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from gym_unity.envs import UnityToGymWrapper

from plotting.plot import plot_ten, plot_hundred, plot_loss

channel = EngineConfigurationChannel()

unity_env = UnityEnvironment('../../New folder/Player Control.exe', side_channels=[channel], seed=42, worker_id=1)
channel.set_configuration_parameters(time_scale=3.0)

env = UnityToGymWrapper(unity_env, True)

state_dim = env._observation_space.shape[0]
action_dim = env._action_space.shape[0]

gamma = 0.99
tau = 0.01
a_lr = 3e-4
q_lr = 3e-4
p_lr = 3e-4
buffer_maxlen = 1000000

max_episode = 2000
max_step = 5000

replay_buffer = ReplayBuffer(capacity=buffer_maxlen)

agent = SACAgent(state_dim, action_dim, replay_buffer)

def discrete_sac_train(env, agent, max_episode, max_step, batch_size):
  episode_rewards = []
  update_step = 0

  for episode in range(max_episode):
    state = env.reset()
    episode_reward = 0

    for step in range(max_step):
      action = agent.get_action(state)
      print('Before numpy: ', type(action))
      next_state, reward, done, _ = env.step(action)
      agent.replay_buffer.push(state, action, reward, next_state, done)
      episode_reward += reward

      if len(agent.replay_buffer) > batch_size:
        agent.update(state, action, next_state, reward, done, batch_size)
        update_step += 1

      if done or step == max_step - 1:
        episode_rewards.append(episode_reward)
        break

      state = next_state

    if episode % 10 == 0:
      print("Episode " + str(episode) + ": " + str(episode_reward))

  return episode_rewards

episode_rewards = discrete_sac_train(env, agent, max_episode, max_step, 128)

plot_ten(max_episode, episode_rewards)
plot_hundred(max_episode, episode_rewards)
