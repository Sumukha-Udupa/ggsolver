"""
This structure should implement Def. 1 from L'CSS paper.
"""
from abc import ABC, abstractmethod
from ggsolver.models import Game
from tqdm import tqdm
from itertools import chain, combinations


State_n = namedtuple("State_n", ["state", "belief", "action", "sigma"])

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


class BeliefGame(Game):
    def __init__(self, game):
        super(BeliefGame, self).__init__(is_tb=True, is_stoch=True, is_quant=False)
        self.game           = game
        self.game_states    = self.game.states()
        self.game_actions   = self.game.actions()
        self.sensor_query   = self.game.p1_query_actions()
        self.sensor_attacks = self.game.p2_attack_actions()
        self.belief_game_actions = self.actions()
        self.final_states   = self.final_states_set()

        
        self.observation_list = list()
        
    def obs_list(self, belief):
        for st in belief:
            self.observation_list.append(State_n(self.game_states[st], frozenset(belief), None, None))
            
    def post_belief(self, belief, act):
        belief_dash = set()
        for st in belief:
            next_states = self.game.delta(st, act)
            if next_states != None:
                belief_dash = belief_dash.union(set(next_states))
            else:
                belief_dash = belief_dash
        return belief_dash


    def states(self):
        # TODO. Construct the set of states using self.game.states().
        belief_set = powerset(set(range(1, len(self.game_states)+1)))
        map(self.obs_list, belief_set)
        # P1 states
        Q_1 = self.observation_list
        # Nature states
        Q_N = list()
        for q1 in tqdm(Q_1):
            for a, sig in itertools.product(self.game.actions, self.sensor_query):
                belief_dash = self.post_belief(q1.belief, a)
                Q_N.append(State_n(q1.state, frozenset(belief_dash), a, sig))
        # P2 states
        Q_2 = list()
        for q0 in tqdm(Q_N):
            post_states = self.game.delta(q0.state, q0.action)
            if post_states != None:
                for s_dash in post_states:
                    Q_2.append(State_n(s_dash, frozenset(q0.belief), None, q0.sigma))

        # final state
        final = State_n(qF, frozenset({qF}), None, None)

        # all the states
        Q = list()
        Q.append(Q_1)
        Q.append(Q_N)
        Q.append(Q_2)
        Q.append(final)
        return Q

    def actions(self):
        #P1 actions ($A x Sigma$)
        p1_actions = list()
        p1_actions = itertools.product(self.game_actions, self.sensor_query)
        return p1_actions

    def final(self, state):
        return True if state in self.game.final_position else False

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
        # P1 state
        if state.action == None and state.sigma == None:
            for action, sigma in act:
                belief_dash = self.post_belief(state.belief, action)
                new_states.append(State_n(state, frozenset(belief_dash), action, sensor_query))
            return new_states
        # Nature player state
        elif state.action != None:
            for action, sigma in act:
                post_states = self.game.delta(state.state, action)
                if set(post_states).issubset(self.final_states):
                    new_states.append(State_n(qF, frozenset({qF}), None, None))
                    return new_states
                elif len(set(post_states).intersection(self.final_states)) == 0:
                    for st_dash in post_states:
                        new_states.append(State_n(st_dash, frozenset(state.belief), None, state.sigma))
                    return new_states
                else:
                    for st_dash in post_states:
                        new_states.append(State_n(st_dash, frozenset(state.belief), None, state.sigma))
                    new_states.append(State_n(qF, frozenset({qF}), None, None))
                    return new_states
        # P2 state - check
        else:
            obs = self.game.observe(state.state, state.sigma, act)
            belief_ddash = state.belief.intersection(set(obs))
            new_states.append(State_n(state.state, belief_ddash, None, None))
            return new_states



