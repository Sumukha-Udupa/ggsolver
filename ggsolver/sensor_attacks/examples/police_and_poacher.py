from ggsolver.sensor_attacks.sensor_attacks_models import SG_PCOF, BeliefGame
from collections import namedtuple
import itertools

Cell = namedtuple("Cell", ["row", "col"])
State = namedtuple("State", ["pol_pos", "pol_time", "lion_pos"])
State_n = namedtuple("State_n", ["state", "belief", "action", "sigma"])


class PolicePoachers(SG_PCOF):
    NODE_PROPERTY = SG_PCOF.NODE_PROPERTY.copy()
    EDGE_PROPERTY = SG_PCOF.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = SG_PCOF.GRAPH_PROPERTY.copy()

    def __init__(self, grows, gcols, lion_pos, police_pos, police_time, sensor_1_pos, sensor_1_dim, sensor_2_pos,
                 sensor_2_dim, sensor_3_pos, sensor_3_dim, sensor_4_pos, sensor_4_dim, sensor_5_pos, sensor_5_dim,
                 sensor_6_pos, sensor_6_dim, final_pos):
        super(PolicePoachers, self).__init__()
        # TODO. Define parameters to construct the game.
        # Gridworld dimensions.
        self.g_num_rows = grows
        self.g_num_cols = gcols

        # Lion initial position.
        self.lion_init_pos = lion_pos

        # Police initial position.
        self.police_init_pos = police_pos
        self.police_time = police_time

        # Sensor position
        self.sensor_pos = dict()
        self.sensor_pos[1] = sensor_1_pos
        self.sensor_pos[2] = sensor_2_pos
        self.sensor_pos[3] = sensor_3_pos
        self.sensor_pos[4] = sensor_4_pos
        self.sensor_pos[5] = sensor_5_pos
        self.sensor_pos[6] = sensor_6_pos

        # Sensor dimensions
        self.sensor_dim = dict()
        self.sensor_dim[1] = sensor_1_dim
        self.sensor_dim[2] = sensor_2_dim
        self.sensor_dim[3] = sensor_3_dim
        self.sensor_dim[4] = sensor_4_dim
        self.sensor_dim[5] = sensor_5_dim
        self.sensor_dim[6] = sensor_6_dim

        # Area covered by the Jungle
        self.cells_covered_by_jungle = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 1), (1, 2), (2, 2), (3, 2), (4, 3), (3, 3),
                                        (2, 3), (3, 4), (4, 4)]

        # Goal position
        self.final_position = final_pos

    def states(self):
        """
        Returns a set of states in the game.
        """
        # TODO. Use parameters to define the states of the game.

        state_list = []

        for p_pos, p_time, l_pos in itertools.product(itertools.product(range(self.g_num_rows), range(self.g_num_cols)),
                                                      range(self.police_time + 1), self.cells_covered_by_jungle):
            state_list.append(State(Cell(p_pos[0], p_pos[1]), p_time, Cell(l_pos[0], l_pos[1])))

        return state_list

    def actions(self):
        """
        Returns a tuple of set of P1 and P2 actions in the game.
        Format: ($A \times \Sigma$, $\calB$)
        """
        player_1_actions = dict()
        player_1_actions['N'] = [1, 0]
        player_1_actions['S'] = [-1, 0]
        player_1_actions['E'] = [0, 1]
        player_1_actions['W'] = [0, -1]

        return player_1_actions

    # @register_property(GRAPH_PROPERTY)
    def p1_query_actions(self):
        # TODO: make this into parameters.
        query_actions = dict()
        query_actions[1] = {1, 2}
        query_actions[2] = {2, 3}
        query_actions[3] = {3, 4}
        query_actions[4] = {4, 5}
        query_actions[5] = {5, 6}

        return query_actions

    def p2_attack_actions(self):
        # TODO: make this into parameters.
        attack_actions = dict()
        attack_actions[1] = {1}
        attack_actions[2] = {2}
        attack_actions[3] = {3}
        attack_actions[4] = {4}
        attack_actions[5] = {5}
        attack_actions[6] = {6}
        attack_actions[7] = {}
        return attack_actions


    def lion_actions(self):
        lion_actions = dict()
        lion_actions['N'] = [1, 0]
        lion_actions['S'] = [-1, 0]
        lion_actions['E'] = [0, 1]
        lion_actions['W'] = [0, -1]
        return lion_actions

    def boundary_gw(self, p1_state):
        return max(min(p1_state.row, self.g_num_rows), 0), max(min(p1_state.col, self.g_num_cols), 0)

    def boundary_jungle(self, p3_state, act):
        state = (p3_state.row, p3_state.col)
        if state in self.cells_covered_by_jungle:
            new_state = p3_state
        else:
            new_state = Cell(p3_state.row-act[0], p3_state.col-act[1])
        return new_state

    def apply_delta_p1(self, state, act):

        p1_acts = self.actions()
        new_p1_state = Cell(state.pol_pos.row + p1_acts[act][0], state.pol_pos.col + p1_acts[act][1])

        new_p1_state = self.boundary_gw(new_p1_state)

        return new_p1_state


    def apply_delta_p3(self, state):

        new_p3_state = list()
        lion_actions = self.lion_actions()
        for i in lion_actions:
            new_state = Cell(state.lion_pos.row + lion_actions[i][0], state.lion_pos.col + lion_actions[i][1])
            new_state = self.boundary_jungle(new_state, lion_actions[i])
            new_p3_state.append(new_state)

        return new_p3_state

    def delta(self, state, act):
        """
        Returns a set of successor states.
        Note: The function must ensure a P1 action is applied to state.
        """

        new_states = list()

        if state.pol_time == 0:
            new_states.append(state)

        else:
            nstate_time = state.pol_time - 1
            nstate_p1   = self.apply_delta_p1(state, act)
            nstate_p3   = self.apply_delta_p3(state)
            for i in nstate_p3:
                # if the police position is the same as the lion's position, new_state = old_state.
                if nstate_p1 == i:
                    new_states.append(state)
                else:
                    new_states.append(State(nstate_p1, nstate_time, i))

        return new_states

    def final(self, state):
        """
        Returns a set of final states.
        """
        return True if state in self.final_position else False

    def sensors(self):
        """
        Returns a set of sensors.
        """
        sensor_list = [1, 2, 3, 4, 5, 6]
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

        for i in range(sensor_dim[1]-1):
            for j in range(sensor_dim[0]-1):
                cells_covered.add((k+1, m))
                k = k + 1
            cells_covered.add((k, m+1))
            m = m + 1

        return cells_covered

    def observe(self, state, query, attack):
        """
        Observation function in LCSS paper.

        state: A state in game.
        query: A subset of sensors.
        attack: A subset of sensors.
        """
        # TODO: implement the removal of repeted beliefs

        # obs = {st for st in self._graph.nodes() if st.uav_pos == state.uav_pos and st.uav_batt == state.uav_batt}
        obs = self.states()
        obs = {st for st in obs if st.pol_pos == state.pol_pos and st.pol_time == state.pol_time}
        # Considering the actions that are not attacked
        sensor_queries = self.p1_sensor_query()
        attack_actions = self.p2_attack_actions()

        if attack == 7:
            active_sensors = sensor_queries[query]
        else:
            active_sensors = sensor_queries[query] - attack_actions[attack]

        # active_sensors = self._sensor_queries[sense_query] - self._sensor_attacks[attack_query]

        for act in active_sensors:
            if state in self.sensor_range(act):
                obs = obs.intersection(self.sensor_range(act))
            else:
                obs = obs.intersection(set(self.states()).difference(self.sensor_range(act)))
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
