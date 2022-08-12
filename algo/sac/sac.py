import torch
from torch.optim import Adam
from torch.distributions import Normal
import torch.nn.functional as F
import numpy as np

from networks import QNetwork, PolicyNetwork
from buffer import ReplayBuffer

class SACAgent:
  def __init__(self, env, gamma, tau, alpha, critic_lr, actor_lr, a_lr, buffer_maxlen, delay_step):
    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    self.env = env
    # self.action_range = [env.action_space.low, env.action_space.high]
    self.obs_dim = env.observation_space.shape[0]
    self.action_dim = env.action_space.shape[0]

    # Hyperparameter
    self.gamma = gamma    ## Discount rate
    self.tau = tau      
    self.update_step = 0
    self.delay_step = delay_step

    # Init network
    ## Critic Net
    self.critic1 = QNetwork(self.obs_dim, self.action_dim).to(self.device)
    self.critic2 = QNetwork(self.obs_dim, self.action_dim).to(self.device)

    ## Actor Net
    self.actor = PolicyNetwork(self.obs_dim, self.action_dim).to(self.device)

    ## Target Net
    self.critic1_target = QNetwork(self.obs_dim, self.action_dim).to(self.device)
    self.critic2_target = QNetwork(self.obs_dim, self.action_dim).to(self.device)
    self.actor_target = PolicyNetwork(self.obs_dim, self.action_dim).to(self.device)

    # Copy params to target
    for target_param, param in zip(self.critic1_target.parameters(), self.critic1.parameters()):
      target_param.data.copy_(param.data)

    for target_param, param in zip(self.critic2_target.parameters(), self.critic2.parameters()):
      target_param.data.copy_(param.data)

    # Init optimizers
    self.critic1_optim = Adam(self.critic1.parameters(), lr=critic_lr)
    self.critic2_optim = Adam(self.critic2.parameters(), lr=critic_lr)
    self.actor_optim = Adam(self.actor.parameters(), lr=actor_lr)

    # Entropy
    self.alpha = alpha    ## Tempature param
    self.target_entropy = -torch.prod(torch.Tensor(self.env.action_space.shape).to(self.device)).item()
    self.log_alpha = torch.zeros(1, requires_grad=True, device=self.device)
    self.alpha_optim = Adam([self.log_alpha], lr=a_lr)

    # ReplayBuffer
    self.replay_buffer = ReplayBuffer(capacity=buffer_maxlen)

  # def rescale_action(self, action):
  #   return action * (self.action_range[1] - self.action_range[0]) / 2.0 + (self.action_range[1] + self.action_range[0]) / 2.0

  def get_action(self, state):
    state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
    action, _, _ = self.actor.sample(state)
    action = action.squeeze(0).cpu().detach().numpy()
    # return np.floor(action + 0.1)
    return action

  def update_targets(self):
    for target_param, param in zip(self.critic1_target.parameters(), self.critic1.parameters()):
      target_param.data.copy_(param.data * self.tau + target_param.data * (1.0 - self.tau))

    for target_param, param in zip(self.critic2_target.parameters(), self.critic2.parameters()):
      target_param.data.copy_(param.data * self.tau + target_param.data * (1.0 - self.tau))

  def update(self, batch_size):
    states, actions, rewards, next_states, dones = self.replay_buffer.sample(batch_size)

    states = torch.FloatTensor(states).to(self.device)
    actions = torch.FloatTensor(actions).to(self.device)
    rewards = torch.FloatTensor(rewards).to(self.device)
    next_states = torch.FloatTensor(next_states).to(self.device)
    dones = torch.FloatTensor(dones).to(self.device)
    dones = dones.view(dones.size(0), -1)

    next_actions, next_log_pi, _ = self.actor.sample(next_states)
    next_q1 = self.critic1_target(next_states, next_actions)
    next_q2 = self.critic2_target(next_states, next_actions)
    next_q_target = torch.min(next_q1, next_q2) - self.alpha * next_log_pi
    expected_q = rewards + (1 - dones) * self.gamma * next_q_target

    # Calculate q loss
    curr_q1 = self.critic1.forward(states, actions)
    curr_q2 = self.critic2.forward(states, actions)
    q1_loss = F.mse_loss(curr_q1, expected_q.detach())
    q2_loss = F.mse_loss(curr_q2, expected_q.detach())

    # Update Q networks
    self.critic1_optim.zero_grad()
    q1_loss.backward()
    self.critic1_optim.step()

    self.critic2.zero_grad()
    q2_loss.backward()
    self.critic2_optim.step()

    # Delayed update for policy network and target q network
    new_actions, log_pi, _ = self.actor.sample(states)
    if self.update_step % self.delay_step == 0:
      min_q = torch.min(self.critic1.forward(states, new_actions), 
                        self.critic2.forward(states, new_actions))
      policy_loss = (self.alpha * log_pi - min_q).mean()
      
      self.actor_optim.zero_grad()
      policy_loss.backward()
      self.actor_optim.step()

      # Target network
      self.update_targets()

    # Update tempature
    alpha_loss = (self.log_alpha * (-log_pi - self.target_entropy).detach()).mean()

    self.alpha_optim.zero_grad()
    alpha_loss.backward()
    self.alpha_optim.step()
    self.alpha = self.log_alpha.exp()

    self.update_step += 1