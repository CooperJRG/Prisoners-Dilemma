import random
import memory
import time


class Strategy:
    DEFAULT_BEHAVIOR_BIT = 63
    RANDOM_ACT_BIT = 62
    COOP_PROB_START_BIT = 57
    DEFECT_PROB_START_BIT = 52
    MEMORY_BIT = 43
    MEMORY_WINDOW_START_BIT = 42
    STRATEGY_BITS_START = 37
    STRATEGY_PROB_START = 7
    MDNA_MASK = 0x7F
    
    def __init__(self, genome):
        self.genome = genome
        self.name = 'strategy'
        self.behavior = self.interpret_strategy(genome)
        self.fitness = 0

    @staticmethod
    def generate_random_strategy():
        genome = random.getrandbits(64)  # Generate a random 64-bit integer
        return Strategy(genome)

    @staticmethod
    def interpret_strategy(genome):
        # Decode the genome to determine the strategy's behavior
        behavior = {
            'default': 'cooperate' if (genome >> Strategy.DEFAULT_BEHAVIOR_BIT) & 0x1 else 'defect',
            'use_random': (genome >> Strategy.RANDOM_ACT_BIT) & 0x1
        }

        # Decode random behavior parameters if random actions are used
        if behavior['use_random']:
            behavior['coop_prob'] = (genome >> Strategy.COOP_PROB_START_BIT & 0x1F) / 31.0
            behavior['defect_prob'] = (genome >> Strategy.DEFECT_PROB_START_BIT & 0x1F) / 31.0

        # Does it have memory?
        behavior['memory'] = (genome >> Strategy.MEMORY_BIT) & 0x1
        # Decode memory window size
        behavior['mem_window'] = max(genome >> Strategy.MEMORY_WINDOW_START_BIT & 0xFF, 1)

        # Decode strategy priorities and probabilities
        strategy_names = ['grudge', 'sorry', 'cc', 'cd', 'dc', 'dd']
        Strategy._decode_strategies(genome, strategy_names, behavior)

        # Decode mDNA
        behavior['mDNA'] = genome & Strategy.MDNA_MASK
        return behavior

    @staticmethod
    def _decode_strategies(genome, strategy_names, behavior):
        # Decoding strategy priorities
        for i, name in enumerate(strategy_names):
            behavior[name] = (genome >> (Strategy.STRATEGY_BITS_START + i)) & 0x1
        # Decoding strategy probabilities
        for i, name in enumerate(strategy_names):
            offset = Strategy.STRATEGY_PROB_START + i * 5
            behavior[name + '_prob'] = (genome >> offset & 0x1F) / 31.0


    def make_decision(self,  history):
        # Use self.behavior to decide based on game history
        # Consider random moves first
        decision = None
        mem_len = 1
        if self.behavior['memory']:
            mem_len = max(1, min(history.get_length(self.name), self.behavior['mem_window']))
            
        history = history.get_interaction_counts(self.name, self.behavior['mem_window'])
        if self.behavior['use_random']:
            decision = self.random_decision()
        if decision is None:
            decision_votes = {'cooperate': 0, 'defect': 0}
            # Consider the strategies
            if self.behavior['grudge']:
                decision_votes[self.grudge_decision(history, mem_len)] += 1
            if self.behavior['sorry']:
                decision_votes[self.sorry_decision(history, mem_len)] += 1
            if self.behavior['cc']:
                decision_votes[self.cc_decision(history, mem_len)] += 1
            if self.behavior['cd']:
                decision_votes[self.cd_decision(history, mem_len)] += 1
            if self.behavior['dc']:
                decision_votes[self.dc_decision(history, mem_len)] += 1
            if self.behavior['dd']:
                decision_votes[self.dd_decision(history, mem_len)] += 1
            # Take a majority vote, behavior['default'] in case of a tie
            max_votes = max(decision_votes.values())
            candidates = [candidate for candidate, votes in decision_votes.items() if votes == max_votes]

            # Take a decision
            if len(candidates) > 1:  # This means there's a tie
                decision = self.behavior['default']
            else:
                decision = max(decision_votes, key=decision_votes.get)
            return decision
        return decision

    def random_decision(self):
        rand = random.random()
        # Determine to consider defection or cooperation first
        if self.behavior['default'] == 'cooperate':
            if rand < self.behavior['coop_prob']:
                return 'cooperate'
            elif rand < self.behavior['defect_prob']:
                return 'defect'
        else:
            if rand < self.behavior['defect_prob']:
                return 'defect'
            elif rand < self.behavior['coop_prob']:
                return 'cooperate'
        return None
    
    def grudge_decision(self, history, mem_len):
        # Return defect if opponent has high defection rate
        opponent_defects = (float)(history['cd'] + history['dd']) / mem_len
        if opponent_defects > self.behavior['grudge_prob']:
            return 'defect'
        return 'cooperate'
    
    def sorry_decision(self, history, mem_len):
        self_defects = (float)(history['dc'] + history['dd']) / mem_len
        if self_defects > self.behavior['sorry_prob']:
            return 'defect'
        return 'cooperate'
    
    def cc_decision(self, history, mem_len):
        cc_frac = (float)(history['cc']) / mem_len
        if cc_frac > self.behavior['cc_prob']:
            return 'defect'
        return 'cooperate'
    
    def cd_decision(self, history, mem_len):
        cd_frac = (float)(history['cd']) / mem_len
        if cd_frac > self.behavior['cd_prob']:
            return 'defect'
        return 'cooperate'
    
    def dc_decision(self, history, mem_len):
        dc_frac = (float)(history['dc']) / mem_len
        if dc_frac > self.behavior['dc_prob']:
            return 'defect'
        return 'cooperate'
    
    def dd_decision(self, history, mem_len):
        dd_frac = (float)(history['dd']) / mem_len
        if dd_frac > self.behavior['dd_prob']:
            return 'defect'
        return 'cooperate'
    
def main():
    # Create a random strategy
    tit_for_tat = Strategy(0b1000000000010000000010000010000000000000000000000000000000000100)
    mem = memory.Memory()
    tit_for_tat.name = 'strategy_one'
    mem.update_memory('strategy_one', 'c')
    mem.update_memory('strategy_two', 'd')
    mem.update_memory('strategy_one', 'c')
    mem.update_memory('strategy_two', 'c')
    mem.update_memory('strategy_one', 'c')
    mem.update_memory('strategy_two', 'c')
    print(tit_for_tat.make_decision(mem))
    print(tit_for_tat.behavior)
    print(bin(tit_for_tat.genome))

if __name__ == "__main__":
    main()
