import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
from gym_unity.envs import UnityToGymWrapper
import numpy as np

from sac_noise import SAC_NoiseAgent

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
buffer_maxlen = 1000000

max_episode = 4000

agent = SAC_NoiseAgent(obs_dim, action_dim, gamma, tau, alpha, q_lr, p_lr, a_lr, noise_std, noise_bound, buffer_maxlen)

agent.load_model('./saved_models/checkpoint.pkl')

def test(max_episode):
    for episode in range(max_episode):
        state = env.reset()
        done = False
        episode_reward = 0

        while not done:
            action = agent.get_action(state)
            _, reward, done, _ = env.step(np.argmax(action))
            episode_reward += reward

        print("Episode " + str(episode) + ": " + str(episode_reward))

    env.close()

test(max_episode)
