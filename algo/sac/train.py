import sys 
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from gym_unity.envs import UnityToGymWrapper

from sac import SACAgent
from plotting.plot import plot_hundred, plot_ten

channel = EngineConfigurationChannel()

unity_env = UnityEnvironment('../../New folder/Player Control.exe', side_channels=[channel], seed=42, worker_id=1)
channel.set_configuration_parameters(time_scale=3.0)

env = UnityToGymWrapper(unity_env, uint8_visual=True)

print(env.action_space)
print(env.action_space.shape)

gamma = 0.99
tau = 0.01
alpha = 0.2
a_lr = 1e-3
critic_lr = 1e-3
actor_lr = 1e-3
delay_step = 2
buffer_maxlen = 1000000

max_episode = 2000
max_step = 5000

agent = SACAgent(env, gamma, tau, alpha, critic_lr, actor_lr, a_lr, buffer_maxlen, delay_step)

def sac_train(env, agent, max_episode, max_step, batch_size):
  episode_rewards = []

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

      if done or step == max_step - 1:
        episode_rewards.append(episode_reward)
        break
      
      state = next_state

    if episode % 10 == 0:
      print("Episode " + str(episode) + ": " + str(episode_reward))

  env.close()

  return episode_rewards

episode_rewards = sac_train(env, agent, max_episode, max_step, 128)

plot_ten(max_episode, episode_rewards)
plot_hundred(max_episode, episode_rewards)