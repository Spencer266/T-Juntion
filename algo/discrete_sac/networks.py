import torch
import torch.nn as nn
import torch.nn.functional as F
class Network(nn.Module):
  def __init__(self, state_dim, hidden_dim, action_dim, output_activation=nn.Identity(), init_w=3e-3):
    super(Network, self).__init__()
    self.init_w = init_w
    self.l1 = nn.Linear(state_dim, hidden_dim)
    self.l2 = nn.Linear(hidden_dim, hidden_dim)
    self.output_layer = nn.Linear(hidden_dim, action_dim)

    self.output_layer.weight.data.uniform_(-init_w, init_w)
    self.output_layer.bias.data.uniform_(-init_w, init_w)

    self.output_activation = output_activation

  def forward(self, state):
    l1_output = F.relu(self.l1(state))
    l2_output = F.relu(self.l2(l1_output))
    output = self.output_activation(self.output_layer(l2_output))
    return output

  def evaluate(self, state):
    action_prob = self.forward(state)
    z = action_prob == 0.0
    z = z.float() * 1e-8
    log_prob = torch.log(action_prob + z)
    return action_prob, log_prob

  def to(self, device):
    return super(Network, self).to(device)