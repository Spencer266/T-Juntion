import numpy as np

class ReplayBuffer:
  def __init__(self, capacity=1000000):
    self.capacity = capacity
    self.buffer = []
    self.position = 0
    self.weights = np.zeros(capacity)
    self.max_weight = 1e-2
    self.delta = 1e-4
    self.indices = None

  def push(self, state, action, reward, next_state, done):
    experience = (state, action, reward, next_state, done)
    if len(self.buffer) < self.capacity:
      self.buffer.append(None)
    self.buffer[self.position] = experience
    self.weights[self.position] = self.max_weight
    self.position = int((self.position + 1) % self.capacity)

  def sample(self, batch_size=100):
    state_batch = []
    action_batch = []
    reward_batch = []
    next_state_batch = []
    done_batch = []
    set_weights = self.weights[:self.position] + self.delta
    probabilities = set_weights / sum(set_weights)
    self.indices = np.random.choice(range(self.position), batch_size, p=probabilities, replace=False)
    batch = [self.buffer[j] for j in self.indices]
    for experience in batch:
      state, action, reward, next_state, done = experience
      state_batch.append(state)
      action_batch.append(action)
      reward_batch.append(reward)
      next_state_batch.append(next_state)
      done_batch.append(done)

    return state_batch, action_batch, reward_batch, next_state_batch, done_batch

  def update_weigths(self, pred_errors):
    max_error = max(pred_errors)
    self.max_weight = max(self.max_weight, max_error)
    self.weights[self.indices] = pred_errors

  def __len__(self):
    return len(self.buffer)
