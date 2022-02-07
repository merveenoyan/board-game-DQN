# -*- coding: utf-8 -*-
"""debug_RL.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17_WJsj0NWeC-6AuZ-9caBnl-4f5BrmbG
"""

import tensorflow as tf
from tensorflow.keras.layers import Dense, Input
from tensorflow import GradientTape
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import initializers
import numpy as np
import random

game_runner = GameRunner(agent_1 = agent_1, agent_2 = agent_2, model = q_network, pieces = pieces, board = board)

game_runner.run()

class GameRunner:
  
  def __init__(self, agent_1, agent_2, model, pieces, board):
    
    self.agent_1 = agent_1
    self.agent_2 = agent_2
    self.model = model
    self.pieces = pieces
    self.steps = 500
    self.board = board
    #self.state = board
    self.next_state = None
    self.min_eps = 0.01
    self.eps = 0.01
    self.max_eps = 1
    self.step = None
    
  def run(self):
      
      epsilon = 0.4
      lambd = 0.0001
      gamma = 0.99
      batch_size = 50
      learning_rate = 0.01
      

      # Define optimizer
      optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

      for current_step in range(self.steps):

          self.step = current_step
          if self.step % 2 == 0:
            agent = self.agent_1

          else:
            agent = self.agent_2


          if agent == self.agent_1:

            with tf.GradientTape() as tape:
                action = self.agent_1.choose_action(self.board, self.step, self.eps)

                q_values = q_network(self.board.flatten())
                
                epsilon = np.random.rand()

                # choose the action

                actions = self.agent_1.get_available_actions(self.board, self.pieces)
        
                if steps < 100:
                    action = random.choice(actions)
                elif steps > 100:
                    if random.random() < self.eps:
                        action = random.choice(actions)
                    else:
                        action = np.argmax(self.model.predict(self.board.flatten()))

                self.eps = self.min_eps + (self.max_eps - self.min_eps) * math.exp(-lambd * self.steps) # update epsilon

                reward = calculate_reward(action)

                q_value = q_values[0, action]
                loss_value = mean_squared_error_loss(q_value, reward)
                grads = tape.gradient(loss_value[0], q_network.trainable_variables)
                optimizer.apply_gradients(zip(grads, q_network.trainable_variables))
            
          else:
            actions = self.agent_2.get_available_actions(self.board, self.pieces, action)


            action = self.agent_2.choose_action(self.board, self.step, self.eps)

            for act in actions:
                
                action_dict = {}
                action_dict[act] = self.calculate_reward(act, pieces)
                action = max(action_dict, key=action_dict.get)

          next_state, reward, done = self.update_state(agent, pieces, board)

          if done:
              next_state = None 
          
          agent_1.memory.add_sample((self.board, action, reward, next_state))
          agent_1.replay()


          board = next_state 
          
          agent_1.total_reward += reward
          
          agent_2.total_reward += reward

          if done:
              self.reward_store.append(total_reward)

          print(f"Step {self.step}, Total reward: {total_reward}, Episodes: {episodes}")


  # experience replay for DQN
  def replay(self):
    batch = self.memory.sample(self.model.batch_size) # take random batch from memory

    states = np.array([val[0] for val in batch])

    next_states = np.array([(np.zeros(self.model.num_states)
                              if val[3] is None else val[3]) for val in batch])

    # predict Q(s,a) given the batch of states
    q_s_a = self.model.predict_on_batch(states)

    q_s_a_d = self.model.predict_on_batch(next_states)

    # setup training arrays
    x = states
    y = np.zeros((len(batch), 196))

    for i, b in enumerate(batch):
        state, action, reward, next_state = b[0], b[1], b[2], b[3]
        
        current_q = q_s_a[i] # current Q value
        
        if next_state is None:
            # when game is done
            current_q[action] = reward
        else: # update Q values
            current_q[action] = reward + gamma * np.amax(q_s_a_d[i])
        
        x[i] = state
        y[i] = current_q
      

  def update_state(self, agent):

      done = False

      for piece in self.pieces:

          if piece.player == 0:
              player_pieces.append(piece)
          else:
              opponent_pieces.append(piece)
      
      if player_pieces == [] or opponent_pieces == []:
          done = True

      board = agent.move(board, action)

      reward = agent.calculate_reward(action, self.pieces)

      next_state = self.get_next_state(self.pieces)

      return next_state, reward, done

class Agent: 
  
  def __init__(self, player, model = None, memory = None):

    self.model = model
    self.memory = memory
    self.player = player # can be 1 or 2, used to match agents with their pieces



    # get the list available actions based on positioning of the pieces
    # each action is a list [increment in x, increment in y, piece itself]

  def get_available_actions(self, board, pieces):
        
    available_actions = []
    player_pieces, opponent_pieces = self.get_pieces(pieces)

    for piece in player_pieces:
        
        if piece.is_on_end == False:

            if board[piece.x + 1, piece.y] == 0:
                available_actions.append((1, 0, piece.x, piece.y))

            elif board[piece.x - 1, piece.y] == 0:
                available_actions.append((-1, 0, piece.x, piece.y))

            elif board[piece.x, piece.y - 1] == 0:
                available_actions.append((0, -1, piece.x, piece.y))

            if board[piece.x, piece.y+1] == 0:
                available_actions.append((0, 1, piece.x, piece.y))
            
        if piece.is_on_end == True:

            if piece.x == 6: # bottom right corner
                if piece.y == 6:
                    if board[ piece.x - 1, piece.y ] == 0: # check if the position next to piece is not occupied
                        available_actions.append([-1, 0, piece])
                    if board[ piece.x, piece.y - 1] == 0:
                        available_actions.append([0, -1, piece])
                
                elif piece.y == 0:  
                    if board[ piece.x - 1, piece.y ] == 0:
                        available_actions.append([-1, 0, piece])
                    
                    if board[ piece.x, piece.y + 1] == 0:
                        available_actions.append([0, 1, piece])
                else:
                    if board[ piece.x - 1, piece.y ] == 0:
                        available_actions.append([-1, 0, piece])
                    if board[ piece.x, piece.y + 1] == 0:
                        available_actions.append([0, 1, piece])
                    if board[ piece.x + 1, piece.y ] == 0:
                        available_actions.append([1, 0, piece])

            if piece.x == 0: # top left corner
                if piece.y == 0: 
                    if board[ piece.x + 1, piece.y] == 0:
                        available_actions.append([1, 0, piece])
                    if board[ piece.x, piece.y + 1] == 0:
                        available_actions.append([0, 1, piece])
                elif piece.y == 6:
                    if board[ piece.x + 1, piece.y ] == 0:
                        available_actions.append([1, 0, piece])
                    if board[ piece.x, piece.y - 1] == 0:
                        available_actions.append([0, -1, piece])
                else:
                    if board[ piece.x + 1, piece.y ] == 0:
                        available_actions.append([1, 0, piece])
                    if board[ piece.x, piece.y + 1] == 0:
                        available_actions.append([0, 1, piece])
                    if board[ piece.x, piece.y - 1] == 0:
                        available_actions.append([0, -1, piece])
        
    return available_actions


  # get reward based on pieces or termination
  def calculate_reward(self, action, pieces):
        
    if self.player == 1:
        opponent = agent_2
    else: 
        opponent = agent_1
    player_pieces, opponent_pieces = self.get_pieces(pieces)

    # | X O 
    # if piece is on edge

    for player_piece in player_pieces:
        for opponent_piece in opponent_pieces:
            
            #defensive

            if player_piece.y == 0 and opponent_piece.y == 0: 
                if player_piece.x == opponent_piece.x - 1:
                    
                    reward = -5
                    #player_piece.discarded = 1 
                    # board[player_piece.x, player_piece.y] = 0
                    # player_pieces.pop(player_piece)

            elif player_piece.y == 6 and opponent_piece.y == 6: 
                if player_piece.x == opponent_piece.x + 1:
                    reward = -5
                    
            elif player_piece.x == 6 and opponent_piece.x == 6: 

                if player_piece.y == opponent_piece.y + 1:
                    reward = -5

            elif player_piece.x == 0 and opponent_piece.x == 0: 

                if player_piece.y == opponent_piece.y - 1:
                    reward = -5

            # aggressive
            if player_piece.y == 0 and opponent_piece.y == 0:
                if player_piece.x == opponent_piece.x + 1:
                    
                    reward = 5
                    # player_piece.discarded = 1 
                    # board[player_piece.x, player_piece.y] = 0
                    # player_pieces.pop(player_piece)

            elif player_piece.y == 6 and opponent_piece.y == 6: # O X |
                if player_piece.x == opponent_piece.x - 1:
                    reward = 5
                    
            elif player_piece.x == 6 and opponent_piece.x == 6: 

                if player_piece.y == opponent_piece.y - 1:
                    reward = 5

            elif player_piece.x == 0 and opponent_piece.x == 0: 

                if player_piece.y == opponent_piece.y + 1:
                    reward = 5

    return reward


    
  # choose reward based action or q-value based action
  def choose_action(self, state, step, eps):
    #import pdb;pdb.set_trace()

    actions = self.get_available_actions(board, pieces)
    print(f"actions is {actions}")
    
    if self.player == 1:

        if step < 100:
            return random.choice(actions)
        elif step > 100:
            #if random.random() < eps:
            #    return random.choice(actions)
            #else:
            return np.argmax(self.model.predict(state))
    else:

        for action in actions:
            action_dict = {}
            action_dict[action] = self.calculate_reward(action, pieces)
            best_move = max(action_dict, key=action_dict.get)
        
        return best_move

  def move(self, board, action, agent):
        
    action = self.choose_action(state = board, step = GameRunner.step, eps = 0.5)

    piece = action[2]

    old_pos = [piece.x, piece.y] # keep old position

    board[piece.x + action[0], piece.y + action[1]] = piece.player # update board
    
    piece.x += action[0] #update piece
    piece.y += action[1]
    
    pieces = pieces.remove(piece)

    board[old_pos[0], old_pos[1]] = 0

    return board


  # get list of pieces for each player
  def get_pieces(self, pieces):

      player_pieces = []
      opponent_pieces = []

      for piece in pieces:
        if self.player == piece.player:
          player_pieces.append(piece)
        else:
          opponent_pieces.append(piece)

      return player_pieces, opponent_pieces

class Piece:

    def __init__(self, x, y, discarded, player):
        self.x = x
        self.y = y
        self.discarded = discarded
        self.player = player

    def is_on_end(self, x, y):
        
        if self.x == 6 or self.x == 0:
            return True
        if self.y == 6 or self.y == 0:
            return True
        else:
            return False

def construct_q_network():

    inputs = tf.keras.layers.Input(shape=(49))  # size of states raveled, board flattened
    hidden1 = tf.keras.layers.Dense(
        128, activation="relu", kernel_initializer=initializers.he_normal()
    )(inputs)
    hidden2 = tf.keras.layers.Dense(
        256, activation="relu", kernel_initializer=initializers.he_normal()
    )(hidden1)
    hidden3 = tf.keras.layers.Dense(
        192, activation="relu", kernel_initializer=initializers.he_normal()
    )(hidden2)
    q_values = tf.keras.layers.Dense(
        196, kernel_initializer=initializers.Zeros(), activation="softmax"
    )(hidden3) # number of actions is board.x * board.y * moves

    deep_q_network = tf.keras.Model(inputs=inputs, outputs=[q_values])

    return deep_q_network

class Memory:
    def __init__(self, max_memory):
        self.max_memory = max_memory
        self.samples = []

    def add_sample(self, sample):
        self.samples.append(sample)
        if len(self.samples) > self.max_memory:
            self.samples.pop(0)

    def sample(self, no_samples):
        if no_samples > len(self._samples):
            return random.sample(self.samples, len(self.samples))
        else:
            return random.sample(self.samples, no_samples)

def init_board():

    board = np.zeros([7,7])

    piece_1_1 = Piece(x = 0, y = 0, discarded = 0, player = 1)
    piece_1_2 = Piece(x = 0, y = 2, discarded = 0, player = 1)
    piece_1_3 = Piece(x = 0, y = 4, discarded = 0, player = 2)
    piece_1_4 = Piece(x = 6, y = 6, discarded = 0, player = 1)

    piece_2_1 = Piece(x = 6, y = 4, discarded = 0, player = 1)
    piece_2_2 = Piece(x = 0, y = 6, discarded = 0, player = 2)
    piece_2_3 = Piece(x = 6, y = 0, discarded = 0, player = 2)
    piece_2_4 = Piece(x = 6, y = 2, discarded = 0, player = 2)

    pieces = [piece_1_1, piece_1_2, piece_1_3, piece_1_4,
              piece_2_1, piece_2_2, piece_2_3, piece_2_4]
    for piece in pieces:

      board[piece.x, piece.y] = piece.player

    return pieces, board

pieces, board = init_board()

board

memory = Memory(max_memory = 100)

q_network = construct_q_network()

q_network.summary()

agent_1 = Agent(player = 1, model = q_network, memory = memory)

agent_2 = Agent(player = 2, model = None,  memory = None)



"""
    # choose reward based action or q-value based action
    def choose_action(self, state, action):

        actions = agent.get_available_actions(board, pieces, action)
        
        if self.player == 1:

            if steps < 100:
                return random.choice(actions)
            elif steps > 100:
                if random.random() < self.eps:
                    return random.choice(actions)
                else:
                    return np.argmax(self.model.predict(state))
        else:

            for action in actions:
                action_dict = {}
                action_dict[action] = self.calculate_reward(action, pieces)
                best_move = max(action_dict, key=action_dict.get)
            
            return best_move
"""



"""

    def __init__(self):

        self.state_dim = state_dim 
        self.action_dim = action_dim
        self.q_values = q_values # Q-values of state, action, a tuple
        self.num_states = num_states # number of potential board configurations
        self.num_actions = num_actions # number of actions, 7*7*4
        self.states = states
        self.actions = None # moving a particular piece to up/down/left/right, a tuple
    



    def add_state(self, states, pieces):

      ## [[state 1], [[piece 1.x, piece 1.y, piece1.player, piece 1.discarded], [piece_2], ...]
      
      piece_states = []

      for piece in self.pieces:

        piece_state = [piece.x, piece.y, piece.player, piece.discarded]
        piece_states.append(piece_state)
      states.append(piece_states)

      return states




    def get_next_state(self, pieces):

      next_state = []

      for piece in self.pieces:

        pieces_state = [piece.x, piece.y, piece.player, piece.discarded]
        next_state.append(pieces_state)
      

      return next_state
"""

