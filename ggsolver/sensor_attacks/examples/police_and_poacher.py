from ggsolver.sensor_attacks.sensor_attacks_models import SG_PCOF, BeliefGame
from collections import namedtuple
import itertools

Cell = namedtuple("Cell", ["row", "col"])
State = namedtuple("State", ["pol_pos", "pol_time", "lion_pos"])
State_n = namedtuple("State_n", ["state", "belief", "action", "sigma"])

jungle_cells = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 1), (1, 2), (2, 2), (3, 2), (4, 3), (3, 3),
                (2, 3), (3, 4), (4, 4)]


class PolicePoachers(SG_PCOF):
    NODE_PROPERTY = SG_PCOF.NODE_PROPERTY.copy()
    EDGE_PROPERTY = SG_PCOF.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = SG_PCOF.GRAPH_PROPERTY.copy()

    def __init__(self, grows, gcols, lion_pos, police_pos, police_time, sensors, sensor_pos, sensor_dim,
                 jungle_cells, p1_actions, p1_query, p2_attack, final_pos):
        super(PolicePoachers, self).__init__()
        # TODO. Define parameters to construct the game.
        # Gridworld dimensions.
        self.g_num_rows = grows
        self.g_num_cols = gcols

        # Player 1 actions - dictionary
        self.p1_actions = p1_actions

        # Lion initial position.
        self.lion_init_pos = lion_pos

        # Police initial position.
        self.police_init_pos = police_pos
        self.police_time = police_time

        # number of sensors
        self.sensors = sensors

        # Sensor position - dictionary
        self.sensor_pos = sensor_pos

        # Sensor dimensions - dictionary
        self.sensor_dim = sensor_dim

        # Area covered by the Jungle
        self.jungle_cells = jungle_cells

        # Goal position
        self.final_position = final_pos

        # States of the game
        self._states = self.states()

        # P1 sensor queries - dict
        self.sensor_queries = p1_query
        self._sensor_queries = self.sensor_queries

        # P2 attack actions
        self.sensor_attack = p2_attack
        self._sensor_attack_actions = self.sensor_attack

    def states(self):
        """
        Returns a set of states in the game.
        """
        # TODO. Use parameters to define the states of the game.

        state_list = []
        for p_pos, p_time, l_pos in itertools.product(itertools.product(range(self.g_num_rows), range(self.g_num_cols)),
                                                      range(self.police_time + 1), self.jungle_cells):
            state_list.append(State(Cell(p_pos[0], p_pos[1]), p_time, Cell(l_pos[0], l_pos[1])))

        return state_list

    def actions(self):
        """
        Returns a tuple of set of P1 and P2 actions in the game.
        Format: ($A$)
        """
        player_1_actions = list()
        for key, value in self.p1_actions:
            player_1_actions.append(key)

        return player_1_actions

    # @register_property(GRAPH_PROPERTY)
    def p1_query_actions(self):
        # TODO: make this into parameters.
        query_actions = list()
        for key, value in self.sensor_queries:
            query_actions.append(value)
        return query_actions

    def p2_attack_actions(self):
        # TODO: make this into parameters.
        attack_actions = list()
        for key, value in self.sensor_attack:
            attack_actions.append(value)
        return attack_actions

    def lion_actions(self):
        lion_actions = dict()
        lion_actions['N'] = [1, 0]
        lion_actions['S'] = [-1, 0]
        lion_actions['E'] = [0, 1]
        lion_actions['W'] = [0, -1]
        return lion_actions

    def bouncy_boundary_gw(self, p1_state):
        return max(min(p1_state.row, self.g_num_rows), 0), max(min(p1_state.col, self.g_num_cols), 0)

    def bouncy_boundary_jungle(self, p3_state, act):
        state = (p3_state.row, p3_state.col)
        if state in self.jungle_cells:
            new_state = p3_state
        else:
            new_state = Cell(p3_state.row - act[0], p3_state.col - act[1])
        return new_state

    def apply_delta_p1(self, state, act):

        p1_acts = self.p1_actions
        new_p1_state = Cell(state.pol_pos.row + p1_acts[act][0], state.pol_pos.col + p1_acts[act][1])

        new_p1_state = self.bouncy_boundary_gw(new_p1_state)

        return new_p1_state

    def apply_delta_p3(self, state):

        new_p3_state = list()
        lion_actions = self.lion_actions()
        for i in lion_actions:
            new_state = Cell(state.lion_pos.row + lion_actions[i][0], state.lion_pos.col + lion_actions[i][1])
            new_state = self.bouncy_boundary_jungle(new_state, lion_actions[i])
            new_p3_state.append(new_state)

        return new_p3_state

    def delta(self, state, act):
        """
        Returns a set of successor states.
        Note: The function must ensure a P1 action is applied to state.
        """

        new_states = list()
        nstate_time = state.pol_time - 1
        nstate_p1 = self.apply_delta_p1(state, act)
        nstate_p3 = self.apply_delta_p3(state)
        for i in nstate_p3:
            # if the police position is the same as the lion's position, new_state = old_state.
            if state.pol_pos == state.lion_pos or nstate_time < 0:
                new_states.append(state)
            else:
                new_states.append(State(nstate_p1, nstate_time, i))

        return new_states

    def final(self, state):
        """
        Returns a set of final states.
        """
        return True if state.pol_pos in self.final_position else False

    def sensors(self):
        """
        Returns a list of sensors.
        """
        sensor_list = range(1, self.sensors+1)
        return sensor_list

    def sensor_range(self, sensor):
        """
        Returns the set of states covered by the given sensor.
        """
        sensor_pos = self.sensor_pos[sensor]
        sensor_dim = self.sensor_dim[sensor]

        cells_covered = set()

        cells_covered.add((sensor_pos[0], sensor_pos[1]))
        k = sensor_pos[0]
        m = sensor_pos[1]

        for i in range(sensor_dim[1] - 1):
            for j in range(sensor_dim[0] - 1):
                cells_covered.add((k + 1, m))
                k = k + 1
            cells_covered.add((k, m + 1))
            m = m + 1

        return cells_covered

    def observe(self, state, query, attack):
        """
        Observation function in LCSS paper.

        state: A state in game.
        query: A subset of sensors.
        attack: A subset of sensors.
        """
        # TODO: implement the removal of repeated beliefs

        # obs = {st for st in self._graph.nodes() if st.uav_pos == state.uav_pos and st.uav_batt == state.uav_batt}
        obs = self._states
        obs = {st for st in obs if st.pol_pos == state.pol_pos and st.pol_time == state.pol_time}
        # Considering the actions that are not attacked
        sensor_queries = self._sensor_queries
        attack_actions = self._sensor_attack_actions

        if attack == 7:
            active_sensors = sensor_queries[query]
        else:
            active_sensors = sensor_queries[query] - attack_actions[attack]

        # active_sensors = self._sensor_queries[sense_query] - self._sensor_attacks[attack_query]

        for active in active_sensors:
            if state in self.sensor_range(active):
                obs = obs.intersection(self.sensor_range(active))
            else:
                obs = obs.intersection(set(self._states).difference(self.sensor_range(active)))
        return obs


if __name__ == "__main__":
    # Base game instance.
    game = PolicePoachers()
    graph = game.graphify()
    graph.save("/path/to/file.game")

    # Belief game construction
    belief_game = BeliefGame(game)
    belief_graph = belief_game.graphify()
    belief_game.save("/path/to/file.game")
