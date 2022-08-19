"""
This structure should implement Def. 1 from L'CSS paper.
"""
from abc import ABC, abstractmethod
from ggsolver.models import Game
from tqdm import tqdm
import itertools
from collections import namedtuple
from ggsolver.util import powerset

State_n = namedtuple("State_n", ["state", "belief", "action", "sigma"])


class ObsSet:
    def __init__(self):
        self._map = dict()

    def add(self, obj):
        if obj in self._map:
            return self._map[obj]

        self._map[obj] = obj
        return obj


class SG_PCOF(Game, ABC):

    @abstractmethod
    def sensors(self):
        pass

    @abstractmethod
    def sensor_range(self, sensor):
        pass

    @abstractmethod
    def observe(self, state, query, attack):
        pass

    @abstractmethod
    def p1_sensor_query(self):
        pass

    @abstractmethod
    def p2_sensor_attack(self):
        pass

    # @abstractmethod
    # def p1_query_actions(self):
    #     pass

    @abstractmethod
    def lion_actions(self):
        pass



class BeliefGame(Game):
    qF = "qF"

    def __init__(self, game):
        super(BeliefGame, self).__init__(is_tb=True, is_stoch=True, is_quant=False)
        self.game = game
        self.game_states = self.game.states()
        self.game_actions = self.game.actions()
        self.sensor_query = self.game.sensor_queries
        self.sensor_attacks = self.game.sensor_attack
        # self.belief_game_actions = self.actions()
        self._final_states = self.final_states_set()
        self.observation_list = self.construct_observation_set()
        # self._states = self.states()



    # def obs_list(self, belief):
    #     for st in belief:
    #         self.observation_list.append(State_n(self.game_states[st], frozenset(belief), None, None))

    def post_belief(self, belief, act):
        belief_dash = set()
        belief_states = self.to_belief_state(belief)
        for st in belief_states:
            if st == State_n(BeliefGame.qF, BeliefGame.qF, None, None):
                next_states = list()
                next_states.append(State_n(BeliefGame.qF, BeliefGame.qF, None, None))
            else:
                next_states = self.game.delta(st, act)
                if next_states != None:
                    belief_dash = belief_dash.union(set(next_states))
                else:
                    belief_dash = belief_dash
        belief_dash_id = self.to_belief_id(belief_dash)
        return belief_dash_id

    def to_belief_id(self, belief):
        # input a belief state and outputs a unique id for the belief state - binary converted to integer.
        if belief == BeliefGame.qF:
            integer_belief_id = -99
        else:
            n = list()
            states = self.game_states
            states.append(State_n(BeliefGame.qF, BeliefGame.qF, None, None))
            for bel in range(len(states)):
                if states[bel] in belief:
                    n.append(1)
                else:
                    n.append(0)

            m = reversed(n)
            binary_id = ''.join(map(str, m))
            integer_belief_id = int(binary_id, 2)
        return integer_belief_id

    def to_belief_state(self, belief_id):
        # input a unique belief state id to obtain the actual belief state
        if belief_id == -99:
            belief_states = list()
            belief_states.append(State_n(BeliefGame.qF, BeliefGame.qF, None, None))
        else:
            belief_states = list()
            states = self.game_states
            states.append(State_n(BeliefGame.qF, BeliefGame.qF, None, None))
            list_iteration_count = 0
            res = [int(i) for i in bin(belief_id)[2:]]
            for i in reversed(res):
                if i == 1:
                    belief_states.append(states[list_iteration_count])
                    list_iteration_count = list_iteration_count+1
                else:
                    list_iteration_count = list_iteration_count+1

            # rev_res = reversed(res)
            # for i in range(len(self.game_states)):
            #     if rev_res[i] == 1:
            #         belief_states.append(self.game_states[i])

        return belief_states

    def construct_observation_set(self):
        obs_set = ObsSet()
        obs_map = dict()
        if not (not self.sensor_attacks):
            for state, query, attack in tqdm(itertools.product(self.game_states, self.sensor_query, self.sensor_attacks)):
                observation = self.game.observe(state, query, attack)
                fobs = obs_set.add(frozenset(observation))
                obs_map[(state, query, attack)] = fobs
                # print(f"\tobs_map[(state, query, attack)]: {obs_map[(state, query, attack)]}, id:{id(fobs)}.")
        else:
            for state, query in tqdm(itertools.product(self.game_states, self.sensor_query)):
                observation = self.game.observe(state, query, None)
                fobs = obs_set.add(frozenset(observation))
                obs_map[(state, query)] = fobs
                # print(f"\tobs_map[(state, query, attack)]: {obs_map[(state, query, attack)]}, id:{id(fobs)}.")
        return obs_map

    def states(self):
        # TODO. Construct the set of states using self.game.states().
        # P1 states
        Q_1  = list()
        # observation_list = self.construct_observation_set()
        for (state_obs_list, sense_query, sense_attack), value in tqdm(self.observation_list.items()):
            # Todo - implement the powerset(o-{s})
            # Player 1 nodes
            power_set_of_belief = powerset(value)
            for B in power_set_of_belief:
                if state_obs_list in B:
                    belief_id_B = self.to_belief_id(list(B))
                    Q_1.append(State_n(state_obs_list, belief_id_B, None, None))

        # Nature states
        Q_N = list()
        for q1 in tqdm(Q_1):
            for a, sig in itertools.product(self.game_actions, self.sensor_query):
                belief_dash = self.post_belief(q1.belief, a)
                Q_N.append(State_n(q1.state, belief_dash, a, sig))
        # P2 states
        Q_2 = list()
        for q0 in tqdm(Q_N):
            post_states = self.game.delta(q0.state, q0.action)
            if post_states != None:
                for s_dash in post_states:
                    Q_2.append(State_n(s_dash, q0.belief, None, q0.sigma))

        # final state - CHECK just giving an integer for qF
        belief_id_final_B = self.to_belief_id(BeliefGame.qF)
        final = State_n(BeliefGame.qF, belief_id_final_B, None, None)

        # all the states
        Q = list()
        Q.extend(Q_1)
        Q.extend(Q_N)
        Q.extend(Q_2)
        Q.append(final)
        return Q

    def turn(self, state):
        current_turn = 1
        if state.action is None and state.sigma is None:
            current_turn = 1
        elif state.action is None and state.sigma is not None:
            current_turn = 2
        else:
            current_turn = 3

        return current_turn

    def actions(self):
        # P1 actions ($A x Sigma$)
        p1_actions = list()
        p1_actions = list(itertools.product(self.game_actions, self.sensor_query))
        return p1_actions

    def final(self, state):
        return True if state.pol_pos == self.game.final_position else False

    def final_states_set(self):
        final_states_set = set()
        for state in self.game_states:
            if self.final(state):
                final_states_set.add(state)
        return final_states_set

    def delta(self, state, act):
        # TODO. Use self.game.delta() to define this function.
        #   Helper functions: `to_belief_id, to_belief_state` are already imported.
        new_states = list()
        print(act)
        # P1 state
        if state.action == None and state.sigma == None:
            belief_dash = self.post_belief(state.belief, act[0])
            new_states.append(State_n(state.state, belief_dash, act[0], act[1]))
            return new_states

        # Nature player state
        elif state.action != None:
            post_states = self.game.delta(state.state, state.action)
            if set(post_states).issubset(self._final_states):
                new_states.append(State_n(BeliefGame.qF, -99, None, None))
                return new_states
            elif len(set(post_states).intersection(self._final_states)) == 0:
                for st_dash in post_states:
                    new_states.append(State_n(st_dash, state.belief, None, state.sigma))
                return new_states
            else:
                for st_dash in post_states:
                    new_states.append(State_n(st_dash, state.belief, None, state.sigma))
                new_states.append(State_n(BeliefGame.qF, -99, None, None))
                return new_states
        # P2 state - check
        elif state.action is None and type(act) != tuple:
            obs = self.game.observe(state.state, state.sigma, act)
            belief_set = set(self.to_belief_state(state.belief))
            belief_ddash = belief_set.intersection(set(obs))
            belief_ddash_id = self.to_belief_id(belief_ddash)
            new_states.append(State_n(state.state, belief_ddash_id, None, None))
            return new_states
