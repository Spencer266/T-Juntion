# -*- coding: utf-8 -*-
import numpy as np
import os

import torch
import torch.nn as nn
from torch.optim import Adam

from networks import Network
from buffer import ReplayBuffer

class DiscreteSAC:
  def __init__(self, state_dim, action_dim, gamma, tau, 
               q_lr, policy_lr, a_lr, buffer_maxlen, hidden_dim=256, device=torch.device( "cuda" if torch.cuda.is_available() else "cpu")):
    self.device = device
    self.state_dim = state_dim
    self.action_dim = action_dim

    # Hyperparameter
    self.gamma = gamma
    self.tau = tau
    self.update_step = 0
    self.delay_step = 2

    # Define Actor
    self.actor = Network(self.state_dim, hidden_dim, self.action_dim, output_activation=nn.Softmax(dim=1)).to(device)

    # Define critic
    self.critic1 = Network(self.state_dim, hidden_dim, self.action_dim).to(device)
    self.critic2 = Network(self.state_dim, hidden_dim, self.action_dim).to(device)

    # Critic target
    self.critic1_target = Network(self.state_dim, hidden_dim, self.action_dim).to(device)
    self.critic2_target = Network(self.state_dim, hidden_dim, self.action_dim).to(device)

    # Critic optimizer
    self.critic1_optim = Adam(self.critic1.parameters(), lr=q_lr)
    self.critic2_optim = Adam(self.critic2.parameters(), lr=q_lr)
    self.actor_optim = Adam(self.actor.parameters(), lr=policy_lr)

    # Copy params to target
    for target_param, param in zip(self.critic1_target.parameters(), self.critic1.parameters()):
        target_param.data.copy_(param.data)

    for target_param, param in zip(self.critic2_target.parameters(), self.critic2.parameters()):
        target_param.data.copy_(param.data)

    # Entropy
    self.target_entropy = 0.98 * -np.log(1 / self.action_dim)
    self.log_alpha = torch.tensor(np.log(1.), requires_grad=True)
    self.alpha = self.log_alpha
    self.alpha_optim = Adam([self.log_alpha], lr=a_lr)

    self.loss = nn.MSELoss(reduction='none')

    # ReplayBuffer
    self.replay_buffer = ReplayBuffer(buffer_maxlen)

    self.log = {'critic_loss': [], 'policy_loss': [], 'entropy_loss': []}

  def get_action(self, state, evaluation_episode=False):
    state = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(self.device)
    action_prob = self.actor.forward(state)
    action_prob = action_prob.squeeze(0).detach().cpu().numpy()

    if evaluation_episode:
      discrete_action = np.argmax(action_prob)
    else:
      discrete_action = np.random.choice(range(self.action_dim), p=action_prob)
    
    return discrete_action

  def update(self, state, action, next_state, reward, done, batch_size, gamma=0.99):
    self.replay_buffer.push(state, action, reward, next_state, done)

    if self.replay_buffer.__len__() >= batch_size:
      states, actions, rewards, next_states, dones = self.replay_buffer.sample(batch_size)

      state = torch.tensor(states, dtype=torch.float32).to(self.device)
      action = torch.tensor(actions, dtype=torch.int64).to(self.device)
      reward = torch.tensor(rewards, dtype=torch.float32).to(self.device)
      next_state = torch.tensor(next_states, dtype=torch.float32).to(self.device)
      done = torch.tensor(dones).to(self.device)

      # Train critic
      with torch.no_grad():
        action_prob, log_prob = self.actor.evaluate(next_state)

        target_q1_val = self.critic1_target.forward(next_state)
        target_q2_val = self.critic2_target.forward(next_state)
        min_q_value = torch.min(target_q1_val, target_q2_val) - self.alpha * log_prob
        soft_state_val = (action_prob + min_q_value).sum(dim=1)
        target_q_val = reward + ~done * gamma * soft_state_val

      predicted_q1_val = self.critic1.forward(state)
      predicted_q2_val = self.critic2.forward(state)

      soft_q1_val = predicted_q1_val.gather(1, action.unsqueeze(-1)).squeeze(-1)
      soft_q2_val = predicted_q2_val.gather(1, action.unsqueeze(-1)).squeeze(-1)

      critic1_loss = self.loss(soft_q1_val, target_q_val)
      critic2_loss = self.loss(soft_q2_val, target_q_val)
      weight_update = [min(l1.item(), l2.item()) for l1, l2 in zip(critic1_loss, critic2_loss)]

      self.replay_buffer.update_weigths(weight_update)

      critic1_loss = critic1_loss.mean()
      critic2_loss = critic2_loss.mean()

      critic_loss = critic1_loss + critic2_loss

      self.critic1_optim.zero_grad()
      critic1_loss.backward()
      self.critic1_optim.step()

      self.critic2_optim.zero_grad()
      critic2_loss.backward()
      self.critic2_optim.step()

      # Train actor
      pi, log_pi = self.actor.evaluate(state)
      expected_new_q1_pi = self.critic1.forward(state)
      expected_new_q2_pi = self.critic2.forward(state)
      expected_new_q_pi = torch.min(expected_new_q1_pi, expected_new_q2_pi)

      inside_term = self.alpha * log_pi - expected_new_q_pi

      actor_loss = (pi * inside_term).sum(dim=1).mean()

      self.actor_optim.zero_grad()
      actor_loss.backward()
      self.actor_optim.step()

      # Tuning entropy
      alpha_loss = -(self.log_alpha * (log_pi + self.target_entropy).detach()).mean()
      self.alpha_optim.zero_grad()
      alpha_loss.backward()
      self.alpha_optim.step()
      self.alpha = self.log_alpha.exp()

      self.log['critic_loss'].append(critic_loss.item())
      self.log['policy_loss'].append(actor_loss.item())
      self.log['entropy_loss'].append(alpha_loss.item())

      for target_param, param in zip(self.critic1_target.parameters(), self.critic1.parameters()):
        target_param.data.copy_(target_param.data * (1.0 - self.tau) + param.data * self.tau)

      for target_param, param in zip(self.critic2_target.parameters(), self.critic2.parameters()):
        target_param.data.copy_(target_param.data * (1.0 - self.tau) + param.data * self.tau)