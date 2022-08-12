# -*- coding: utf-8 -*-
import numpy as np
import os

os.environ['CUDA_VISIBLE_DEVICES'] = "0"
os.environ['CUDA_LAUNCH_BLOCKING'] = "1"

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from networks import Network
from utils import *

class SACAgent:
    def __init__(self, state_dim, action_dim, replay_buffer, hidden_dim=256,
                 device=torch.device( "cuda:0" if torch.cuda.is_available() else "cpu")):
        self.device = device
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.replay_buffer = replay_buffer

        self.critic1 = Network(state_dim, hidden_dim, action_dim).to(device)
        self.critic2 = Network(state_dim, hidden_dim, action_dim).to(device)
        self.critic1_target = Network(state_dim, hidden_dim, action_dim).to(device)
        self.critic2_target = Network(state_dim, hidden_dim, action_dim).to(device)
        self.critic1_optim = optim.Adam(self.critic1.parameters(), lr=3e-4)
        self.critic2_optim = optim.Adam(self.critic2.parameters(), lr=3e-4)

        self.actor = Network(state_dim, hidden_dim, action_dim, output_activation=nn.Softmax(dim=1)).to(device)
        self.actor_optim = optim.Adam(self.actor.parameters(), lr=3e-3)

        self.target_entropy = 0.98 * -np.log(1 / action_dim)
        self.log_alpha = torch.tensor(np.log(1.), requires_grad=True)
        self.alpha = self.log_alpha
        self.alpha_optim = torch.optim.Adam([self.log_alpha], lr=1e-4)

        self.loss = nn.MSELoss(reduction="none")

        soft_update(self.critic1_target, self.critic1)
        soft_update(self.critic2_target, self.critic2)
    
    def get_action(self, state, evaluation_episode=False):
        state = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(self.device)
        # print('state', state)
        action_prob = self.actor.forward(state)
        # print('action_prob', action_prob)
        action_prob = action_prob.squeeze(0).detach().cpu().numpy()
        # print(action_prob)
        if evaluation_episode:
            discrete_action = np.argmax(action_prob)
        else:
            discrete_action = np.random.choice(range(self.action_dim), p=action_prob)
        return discrete_action

    def update_model(self, state, action, next_state, reward, done,
                     batch_size=128, gamma=0.99):
        # print('minh1: ', next_state)
        self.replay_buffer.push(state, action, reward, next_state, done)
        
        if self.replay_buffer.get_size() >= batch_size:
            
            state, action, reward, next_state, done = self.replay_buffer.sample(batch_size)

            state = torch.tensor(state, dtype=torch.float32).to(self.device)
            action = torch.tensor(action, dtype=torch.int64).to(self.device)
            reward = torch.tensor(reward, dtype=torch.float32).to(self.device)
            next_state = torch.tensor(next_state, dtype=torch.float32).to(self.device)
            done = torch.tensor(done).to(self.device)
            
            # print("action: ", action)

            # Training Critic
            with torch.no_grad():
                action_prob, log_prob = self.actor.evaluate(next_state)
               
                target_q1_value = self.critic1_target.forward(next_state)
                target_q2_value = self.critic2_target.forward(next_state)
                min_q_value = torch.min(target_q1_value, target_q2_value) - self.alpha * log_prob
                soft_state_value = (action_prob * min_q_value).sum(dim=1)
                target_q_value = reward + ~done * gamma * soft_state_value

            predicted_q1_value = self.critic1.forward(state)
            predicted_q2_value = self.critic2.forward(state)

            soft_q1_value = predicted_q1_value.gather(1, action.unsqueeze(-1)).squeeze(-1)
            soft_q2_value = predicted_q2_value.gather(1, action.unsqueeze(-1)).squeeze(-1)

            critic1_loss = self.loss(soft_q1_value, target_q_value)
            critic2_loss = self.loss(soft_q2_value, target_q_value)
            weight_update = [min(l1.item(), l2.item()) for l1, l2 in zip(critic1_loss, critic2_loss)]
            # print("w: ", weight_update, weight_update[0])
            self.replay_buffer.update_weights(weight_update)
            critic1_loss = critic1_loss.mean()
            critic2_loss = critic2_loss.mean()
            
            self.critic1_optim.zero_grad()
            self.critic2_optim.zero_grad()
            critic1_loss.backward()
            critic2_loss.backward()
            self.critic1_optim.step()
            self.critic2_optim.step()

            # Traning Actor
            pi, log_pi = self.actor.evaluate(state)
            expected_new_q1_pi = self.critic1.forward(state)
            expected_new_q2_pi = self.critic2.forward(state)
            expected_new_q_pi = torch.min(expected_new_q1_pi, expected_new_q2_pi)

            inside_term = self.alpha * log_pi - expected_new_q_pi

            actor_loss = (pi * inside_term).sum(dim=1).mean()
            
            self.actor_optim.zero_grad()
            actor_loss.backward()
            self.actor_optim.step()

            # Entropy Adjusment for Maximum Entropy RL
            alpha_loss = -(self.log_alpha * (log_pi + self.target_entropy).detach()).mean()
            self.alpha_optim.zero_grad()
            alpha_loss.backward()
            self.alpha_optim.step()
            self.alpha = self.log_alpha.exp()

            soft_update(self.critic1_target, self.critic1)
            soft_update(self.critic2_target, self.critic2)