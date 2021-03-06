import torch
import torch.nn as nn
import torch.nn.functional as F

# code from https://github.com/ikostrikov/pytorch-a3c/blob/master/model.py
from gym.spaces import Discrete


def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_normal_(m.weight.data)
        m.bias.data.fill_(0)


class ActorCriticNetwork(torch.nn.Module):
    def __init__(self, n_inputs, action_space, is_discrete=False):
        super(ActorCriticNetwork, self).__init__()

        self.is_discrete = is_discrete
        self.action_space = action_space

        # network architecture specification
        fc1_out = 100
        #fc2_out = 128
        # fc_tower_out defines the number of units after the tower forward pass
        fc_tower_out = fc1_out

        self.fc1 = nn.Linear(n_inputs, fc1_out)
        self.dropout1 = nn.Dropout(0.5)
        #self.fc2 = nn.Linear(fc1_out, fc2_out)
        #self.dropout2 = nn.Dropout(0.5)

        # Define the two heads of the network
        # -----------------------------------

        # * Value head
        # The value head has only 1 output
        self.critic_linear = nn.Linear(fc_tower_out, 1)

        # * Policy head
        # Define the number of output for the policy
        n_outputs = action_space.n if isinstance(action_space, Discrete) else action_space.shape[0]

        if self.is_discrete:
            # in the dicrete case it has
            self.actor_linear = nn.Linear(fc_tower_out, n_outputs)
        else:
            # in the continuous case it has one output for the mu and one for the sigma variable
            # later the workers can sample from a normal distribution
            self.mu = nn.Linear(fc_tower_out, n_outputs)
            self.sigma = nn.Linear(fc_tower_out, n_outputs)

        # initialize the weights using Xavier initialization
        self.apply(init_weights)
        self.train()

    def forward(self, inputs):
        """
        Defines the forward pass of the network.

        :param inputs: Input array object which sufficiently represents the full state of the environment.
        :return: In the discrete case: value, policy
                 In the continuous case: value, mu, sigma
        """
        x = F.relu(self.fc1(inputs.float()))
        x = self.dropout1(x)
        #x = F.relu(self.fc2(x))
        #x = self.dropout2(x)

        if self.is_discrete:
            return self.critic_linear(x), self.actor_linear(x)
        else:
            mu = 24 * torch.tanh(self.mu(x))
            sigma = F.softplus(self.sigma(x)) + 1e-5
            return self.critic_linear(x), mu, sigma
