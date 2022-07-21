import torch
from torch.optim import Adam
import torch.nn.functional as F

from buffer import ReplayBuffer
from networks import QNetwork, PolicyNetwork

class TD3Agent:
  def __init__(self, env, gamma, tau, buffer_maxlen, delay_step, noise_std, noise_bound, critic_lr, actor_lr):
    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    self.env = env

    print('Action obs: ', env.action_space.shape)

    self.state_dim = env.observation_space.shape[0]
    self.action_dim = env.action_space.shape[0]

    # Hyperparam
    self.gamma = gamma          # Discount factor
    self.tau = tau
    self.noise_std = noise_std
    self.noise_bound = noise_bound
    self.update_step = 0
    self.delay_step = delay_step

    # Init actor and critic network
    self.critic1 = QNetwork(self.state_dim, self.action_dim).to(self.device)
    self.critic2 = QNetwork(self.state_dim, self.action_dim).to(self.device)
    self.critic1_target = QNetwork(self.state_dim, self.action_dim).to(self.device)
    self.critic2_target = QNetwork(self.state_dim, self.action_dim).to(self.device)

    self.actor = PolicyNetwork(self.state_dim, self.action_dim).to(self.device)
    self.actor_target = PolicyNetwork(self.state_dim, self.action_dim).to(self.device)

    # Copy critic target parameters
    for target_param, param in zip(self.critic1_target.parameters(), self.critic1.parameters()):
      target_param.data.copy_(param.data)

    for target_param, param in zip(self.critic2_target.parameters(), self.critic2.parameters()):
      target_param.data.copy_(param.data)

    # Init optimizer
    self.critic1_optim = Adam(self.critic1.parameters(), lr=critic_lr)
    self.critic2_optim = Adam(self.critic2.parameters(), lr=critic_lr)
    self.actor_optim = Adam(self.actor.parameters(), lr=actor_lr)

    self.replay_buffer = ReplayBuffer(capacity=buffer_maxlen)

  def get_action(self, state):
    state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
    action = self.actor.forward(state)
    action = action.squeeze(0).cpu().detach().numpy()

    return action

  def generate_action_space_noise(self, action_batch):
    noise = torch.normal(torch.zeros(action_batch.size()), self.noise_std).clamp(-self.noise_bound, self.noise_bound).to(self.device)
    return noise

  def update_targets(self):
    for target_param, param in zip(self.critic1_target.parameters(), self.critic1.parameters()):
      target_param.data.copy_(param.data * self.tau + target_param.data * (1.0 - self.tau))

    for target_param, param in zip(self.critic2_target.parameters(), self.critic2.parameters()):
      target_param.data.copy_(param.data * self.tau + target_param.data * (1.0 - self.tau))
        
    for target_param, param in zip(self.actor_target.parameters(), self.actor.parameters()):
      target_param.data.copy_(param.data * self.tau + target_param.data * (1.0 - self.tau))

  def update(self, batch_size):
    state_batch, action_batch, reward_batch, next_state_batch, masks = self.replay_buffer.sample(batch_size)
    state_batch = torch.FloatTensor(state_batch).to(self.device)
    action_batch = torch.FloatTensor(action_batch).to(self.device)
    reward_batch = torch.FloatTensor(reward_batch).to(self.device)
    next_state_batch = torch.FloatTensor(next_state_batch).to(self.device)
    masks = torch.FloatTensor(masks).to(self.device)

    action_space_noise = self.generate_action_space_noise(action_batch)
    next_actions = self.actor.forward(state_batch) + action_space_noise
    next_Q1 = self.critic1_target.forward(next_state_batch, next_actions)
    next_Q2 = self.critic2_target.forward(next_state_batch, next_actions)
    expected_Q = reward_batch + self.gamma * torch.min(next_Q1, next_Q2)

    # Critic loss
    curr_Q1 = self.critic1.forward(state_batch, action_batch)
    curr_Q2 = self.critic2.forward(state_batch, action_batch)
    critic1_loss = F.mse_loss(curr_Q1, expected_Q.detach())
    critic2_loss = F.mse_loss(curr_Q2, expected_Q.detach())

    # Update critic
    self.critic1_optim.zero_grad()
    critic1_loss.backward()
    self.critic1_optim.step()

    self.critic2_optim.zero_grad()
    critic2_loss.backward()
    self.critic2_optim.step()

    # Delay update for actor and target networks
    if self.update_step % self.delay_step == 0:
      self.actor_optim.zero_grad()
      policy_gradient = -self.critic1(state_batch, self.actor(state_batch)).mean()
      policy_gradient.backward()
      self.actor_optim.step()

      self.update_targets()

    self.update_step += 1