import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal

## Act as Actor
class PolicyNetwork(nn.Module):
  def __init__(self, num_inputs, num_actions, hidden_dim=256, init_w=3e-3, log_std_min=-20, log_std_max=2):
    super(PolicyNetwork, self).__init__()
    self.log_std_min = log_std_min
    self.log_std_max = log_std_max

    self.linear1 = nn.Linear(num_inputs, hidden_dim)
    self.linear2 = nn.Linear(hidden_dim, hidden_dim)

    self.mean_linear = nn.Linear(hidden_dim, num_actions)
    self.mean_linear.weight.data.uniform_(-init_w, init_w)
    self.mean_linear.bias.data.uniform_(-init_w, init_w)

    self.log_std_linear = nn.Linear(hidden_dim, num_actions)
    self.log_std_linear.weight.data.uniform_(-init_w, init_w)
    self.log_std_linear.bias.data.uniform_(-init_w, init_w)

    self.action_scale = torch.tensor(1.)
    self.action_bias = torch.tensor(0.)

  def forward(self, state):
    x = F.relu(self.linear1(state))
    x = F.relu(self.linear2(x))

    mean = self.mean_linear(x)
    log_std = self.log_std_linear(x)
    log_std = torch.clamp(log_std, min=self.log_std_min, max=self.log_std_max)

    return mean, log_std

  def sample(self, state, epsilon=1e-6):
    mean, log_std = self.forward(state)
    std = log_std.exp()

    normal = Normal(mean, std)
    z = normal.rsample()            # Reparameterization (mean + std * N(0,1))
    action = torch.tanh(z)
    action = action * self.action_scale + self.action_bias

    # Enforcing action bound
    log_pi = normal.log_prob(z) - torch.log(1 - action.pow(2) + epsilon)
    log_pi = log_pi.sum(1, keepdim=True)
    mean = torch.tanh(mean) * self.action_scale + self.action_bias

    return action, log_pi, mean

  def to(self, device):
    self.action_scale = self.action_scale.to(device)
    self.action_bias = self.action_bias.to(device)
    return super(PolicyNetwork, self).to(device)