from td3 import TD3Agent
from utils import plot_hundred

gamma = 0.9
tau = 0.01
critic_lr = 1e-3
actor_lr = 1e-3
noise_std = 0.2
noise_bound = 0.5
delay_step = 2
buffer_maxlen = 1000000

max_episode = 2000

agent = TD3Agent(env, gamma, tau, buffer_maxlen, delay_step, noise_std, noise_bound, critic_lr, actor_lr)

def td3_train(env, agent, max_episode, max_step, batch_size):
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

  return episode_rewards

episode_rewards = td3_train(env, agent, max_episode, 500, 128)

plot_hundred(episode_rewards, max_episode)

