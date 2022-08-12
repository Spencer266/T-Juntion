import numpy as np

class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.position = 0
        self.weights = np.zeros(int(capacity))
        self.indices = None
        self.delta = 1e-4
        self.max_weight = 1e-2

    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        self.buffer[self.position] = (state, action, reward, next_state, done)
        self.weights[self.position] = self.max_weight
        self.position = int((self.position + 1) % self.capacity)

    def sample(self, batch_size):
        state = [None]*batch_size; action = [None]*batch_size; reward = [None]*batch_size
        next_state = [None]*batch_size; done = [None]*batch_size
        set_weights = self.weights[:self.position] + self.delta
        prob = set_weights / sum(set_weights)
        self.indices = np.random.choice(range(self.position), batch_size, p=prob, replace=False)
        batch = [self.buffer[x] for x in self.indices]
        for i in range(batch_size):
            state[i], action[i], reward[i], next_state[i], done[i] = batch[i]
            state[i] = state[i].tolist(); next_state[i] = next_state[i].tolist()

        state, action, reward, next_state, done = map(lambda x : np.stack(x), (state, action, reward, next_state, done))
        
        return state, action, reward, next_state, done

    def update_weights(self, prediction_errors):
        max_error = max(prediction_errors)
        self.max_weight = max(self.max_weight, max_error)
        self.weights[self.indices] = prediction_errors

    def get_size(self):
        return self.position

def hard_update(target, source):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(param.data)

def soft_update(target, source, tau=5e-3):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(target_param.data * (1.0 - tau) + param.data * tau)