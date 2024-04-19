class Memory:
    def __init__(self):
        self.history = {}

    def update_memory(self, strategy_name, outcome):
        """
        Update the game history for a given strategy with the outcome of the latest round.

        :param strategy_name: The name of the strategy (e.g., 'strategy_one')
        :param outcome: Outcome of the latest round ('c' for cooperate, 'd' for defect)
        """
        if strategy_name not in self.history:
            self.history[strategy_name] = []
        self.history[strategy_name].append(outcome)
        
    def get_length(self, strategy_name):
        """
        Get the length of the history for a given strategy.

        :param strategy_name: The name of the strategy.
        :return: The length of the history for the specified strategy.
        """
        if strategy_name in self.history:
            return len(self.history[strategy_name])
        return 1
    
    def score(self):
        """
        Calculate the score of the game history.

        :return: A tuple with the scores for strategy one and strategy two.
        """
        if 'strategy_one' not in self.history or 'strategy_two' not in self.history:
            return 0, 0

        score_one = 0
        score_two = 0
        for move_one, move_two in zip(self.history['strategy_one'], self.history['strategy_two']):
            if move_one == 'c' and move_two == 'c':
                score_one += 3
                score_two += 3
            elif move_one == 'c' and move_two == 'd':
                score_one += 0
                score_two += 5
            elif move_one == 'd' and move_two == 'c':
                score_one += 5
                score_two += 0
            elif move_one == 'd' and move_two == 'd':
                score_one += 1
                score_two += 1

        return score_one, score_two

    def get_interaction_counts(self, strategy_name, memory_window):
        """
        Retrieve counts of different interaction types within the specified memory window.

        :param strategy_name: The name of the strategy querying the data.
        :param opponent_name: The name of the opponent strategy.
        :param memory_window: Number of recent rounds to consider.
        :return: Dictionary with counts of 'cc', 'cd', 'dc', and 'dd' interactions.
        """
        if strategy_name not in self.history:
            return {'cc': 0, 'cd': 0, 'dc': 0, 'dd': 0}
        
        if strategy_name == 'strategy_one':
            opponent_name = 'strategy_two'
        else:
            opponent_name = 'strategy_one'

        # Get the last 'memory_window' elements from each strategy's history
        strategy_history = self.history[strategy_name][-memory_window:]
        opponent_history = self.history[opponent_name][-memory_window:]

        interaction_counts = {'cc': 0, 'cd': 0, 'dc': 0, 'dd': 0}
        for strategy_move, opponent_move in zip(strategy_history, opponent_history):
            interaction_type = strategy_move + opponent_move
            if interaction_type in interaction_counts:
                interaction_counts[interaction_type] += 1

        return interaction_counts