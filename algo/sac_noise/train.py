from sac_noise import SAC_NoiseAgent
from utils.plot import plot_hundred

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from gym_unity.envs import UnityToGymWrapper

channel = EngineConfigurationChannel()

unity_env = UnityEnvironment('../../New folder/Player Control.exe', side_channels=[channel], seed=42, worker_id=1)
channel.set_configuration_parameters(time_scale=20.0)

env = UnityToGymWrapper(unity_env, True)

gamma = 0.99
tau = 0.01
alpha = 0.2
a_lr = 3e-4
q_lr = 3e-4
p_lr = 3e-4
noise_std = 0.2
noise_bound = 0.5
delay_step = 2
buffer_maxlen = 1000000

max_episode = 2000

def sac_noise_train(env, agent, max_episode, max_step, batch_size):
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

agent = SAC_NoiseAgent(env, gamma, tau, alpha, q_lr, p_lr, a_lr, delay_step, noise_std, noise_bound, buffer_maxlen)

episode_rewards = sac_noise_train(env, agent, max_episode, 500, 64)

plot_hundred(max_episode, episode_rewards)