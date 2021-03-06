import torch
from torch.optim import Adam
import torch.nn.functional as F

from networks import QNetwork, PolicyNetwork

class SAC_NoiseAgent:
  def __init__(self, env, gamma, tau, alpha, q_lr, policy_lr, a_lr, delay_step, noise_std, noise_bound, buffer_maxlen):
    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    self.env = env
    self.action_range = [env.action_space.low, env.action_space.high]

    # Hyperparameter
    self.gamma = gamma    ## Discount rate
    self.tau = tau      
    self.update_step = 0
    self.delay_step = delay_step

    self.noise_std = noise_std
    self.noise_bound = noise_bound

    # Init network
    ## Critic Net
    self.q_net1 = QNetwork(env.observation_space.shape[0], env.action_space.shape[0]).to(self.device)
    self.q_net2 = QNetwork(env.observation_space.shape[0], env.action_space.shape[0]).to(self.device)

    ## Actor Net
    self.policy_net = PolicyNetwork(env.observation_space.shape[0], env.action_space.shape[0]).to(self.device)

    ## Target Net
    self.target_net1 = QNetwork(env.observation_space.shape[0], env.action_space.shape[0]).to(self.device)
    self.target_net2 = QNetwork(env.observation_space.shape[0], env.action_space.shape[0]).to(self.device)

    # Copy params to target
    for target_param, param in zip(self.target_net1.parameters(), self.q_net1.parameters()):
      target_param.data.copy_(param.data)

    for target_param, param in zip(self.target_net2.parameters(), self.q_net2.parameters()):
      target_param.data.copy_(param.data)

    # Init optimizers
    self.q1_optimizer = Adam(self.q_net1.parameters(), lr=q_lr)
    self.q2_optimizer = Adam(self.q_net2.parameters(), lr=q_lr)
    self.policy_optimizer = Adam(self.policy_net.parameters(), lr=policy_lr)

    # Entropy
    self.alpha = alpha    ## Tempature param
    self.target_entropy = -torch.prod(torch.Tensor(self.env.action_space.shape).to(self.device)).item()
    self.log_alpha = torch.zeros(1, requires_grad=True, device=self.device)
    self.alpha_optim = Adam([self.log_alpha], lr=a_lr)

    # ReplayBuffer
    self.replay_buffer = ReplayBuffer(buffer_maxlen)

  def rescale_action(self, action):
    return action * (self.action_range[1] - self.action_range[0]) / 2.0 + (self.action_range[1] + self.action_range[0]) / 2.0

  # From TD3  
  def generate_action_space_noise(self, action_batch):
    noise = torch.normal(torch.zeros(action_batch.size()), self.noise_std).clamp(-self.noise_bound, self.noise_bound).to(self.device)
    return noise

  def get_action(self, state):
    state = torch.FloatTensor(state).to(self.device).unsqueeze(0)
    mean, log_std = self.policy_net.forward(state)
    std = log_std.exp()

    normal = Normal(mean, std)
    z = normal.sample()
    action = torch.tanh(z)
    action = action.cpu().detach().squeeze(0).numpy()

    return self.rescale_action(action)

  def update(self, batch_size):
    states, actions, rewards, next_states, dones = self.replay_buffer.sample(batch_size)

    states = torch.FloatTensor(states).to(self.device)
    actions = torch.FloatTensor(actions).to(self.device)
    rewards = torch.FloatTensor(rewards).to(self.device)
    next_states = torch.FloatTensor(next_states).to(self.device)
    dones = torch.FloatTensor(dones).to(self.device)
    dones = dones.view(dones.size(0), -1)

    action_space_noise = self.generate_action_space_noise(actions)

    next_actions, next_log_pi, _ = self.policy_net.sample(next_states)
    next_actions = next_actions + action_space_noise
    next_q1 = self.target_net1(next_states, next_actions)
    next_q2 = self.target_net2(next_states, next_actions)
    next_q_target = torch.min(next_q1, next_q2) - self.alpha * next_log_pi
    expected_q = rewards + (1 - dones) * self.gamma * next_q_target

    # Calculate q loss
    curr_q1 = self.q_net1.forward(states, actions)
    curr_q2 = self.q_net2.forward(states, actions)
    q1_loss = F.mse_loss(curr_q1, expected_q.detach())
    q2_loss = F.mse_loss(curr_q2, expected_q.detach())

    # Update Q networks
    self.q1_optimizer.zero_grad()
    q1_loss.backward()
    self.q1_optimizer.step()

    self.q2_optimizer.zero_grad()
    q2_loss.backward()
    self.q2_optimizer.step()

    # Delayed update for policy network and target q network
    new_actions, log_pi, _ = self.policy_net.sample(states)
    if self.update_step % self.delay_step == 0:
      min_q = torch.min(self.q_net1.forward(states, new_actions), 
                        self.q_net2.forward(states, new_actions))
      policy_loss = (self.alpha * log_pi - min_q).mean()
      
      self.policy_optimizer.zero_grad()
      policy_loss.backward()
      self.policy_optimizer.step()

      # Target network
      for target_param, param in zip(self.target_net1.parameters(), self.q_net1.parameters()):
        target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

      for target_param, param in zip(self.target_net2.parameters(), self.q_net2.parameters()):
        target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

    # Update tempature
    alpha_loss = (self.log_alpha * (-log_pi - self.target_entropy).detach()).mean()

    self.alpha_optim.zero_grad()
    alpha_loss.backward()
    self.alpha_optim.step()
    self.alpha = self.log_alpha.exp()

    self.update_step += 1