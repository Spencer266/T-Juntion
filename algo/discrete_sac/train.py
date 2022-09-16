import sys 
import os

from discrete_sac import DiscreteSAC

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from gym_unity.envs import UnityToGymWrapper

from plotting.plot import plot_ten, plot_hundred, plot_loss

channel = EngineConfigurationChannel()

unity_env = UnityEnvironment('../../New folder/Player Control.exe', side_channels=[channel], seed=42, worker_id=1)
channel.set_configuration_parameters(time_scale=3.0)

env = UnityToGymWrapper(unity_env, True)

state_dim = env.observation_space.shape[0]
action_dim = env.action_space.n

gamma = 0.99
tau = 0.01
a_lr = 1e-3
q_lr = 1e-3
policy_lr = 1e-3
buffer_maxlen = 1000000

max_episode = 4000

max_step = 1000

agent = DiscreteSAC(state_dim, action_dim, gamma, tau, q_lr, policy_lr, a_lr, buffer_maxlen)

def discrete_sac_train(max_episode, max_step, batch_size):
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
        agent.update(state, action, next_state, reward, done, batch_size)
        update_step += 1

      if done or step == max_step - 1:
        episode_rewards.append(episode_reward)
        break

      state = next_state

    if episode % 10 == 0:
      print("Episode " + str(episode) + ": " + str(episode_reward))

  return episode_rewards

episode_rewards = discrete_sac_train(max_episode, max_step, 128)

q_loss = agent.log['critic_loss']
p_loss = agent.log['policy_loss']
entropy_loss = agent.log['entropy_loss']

plot_ten(max_episode, episode_rewards)
plot_hundred(max_episode, episode_rewards)
plot_loss(max_episode, q_loss, 'Critic loss')
plot_loss(max_episode, p_loss, 'Policy loss')
plot_loss(max_episode, entropy_loss, 'Entropy loss')

