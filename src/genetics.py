from strategy import Strategy
import numpy as np
import memory
import time

def count_different_bits(x, y):
    # Apply XOR between x and y
    xor_result = x ^ y
    
    # Count and return the number of '1's in the binary representation of xor_result
    return bin(xor_result).count('1')

class GeneticAlgorithm:
    SELECTIVE_PRESSURE = 1.2
    BIT_LENGTH = 57
    
    def __init__(self, population_size, mutation_rate, crossover_rate):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.population = self.initialize_population()
        self.sample_distribution = self.generate_distribution()

    def generate_distribution(self):
        # Generate linear distribution for rank selection
        distribution = np.array([self.prob_linear_rank(i + 1) for i in range(self.population_size)])
        return distribution
    
    def prob_linear_rank(self, i):
        # Calculate probability for rank selection
        n = self.population_size
        sp = GeneticAlgorithm.SELECTIVE_PRESSURE
        return (1/n) * (sp - (2*sp - 2) * ((i - 1) / (n - 1)))

    def initialize_population(self):
        # Initialize population with random strategies
        generation = []
        for _ in range(self.population_size):
            generation.append(Strategy.generate_random_strategy())
        return generation

    def select(self):
        # Implement selection logic - Rank Selection
        # Assume that the population is sorted by fitness
        sampled_array = np.random.choice(self.population, size=2, replace=True, p=self.sample_distribution)
        return sampled_array

    def crossover(self, parent1, parent2):
        # Implement crossover logic - Two-point crossover
        # Two random crossover points
        point_x = np.random.randint(0, GeneticAlgorithm.BIT_LENGTH)
        point_y = np.random.randint(0, GeneticAlgorithm.BIT_LENGTH)
        while point_x == point_y:
            point_y = np.random.randint(0, GeneticAlgorithm.BIT_LENGTH)

        # Ensure point_x is less than point_y
        if point_x > point_y:
            point_x, point_y = point_y, point_x

        # Create new offspring by combining segments from both parents
        mask1 = (1 << point_y) - (1 << point_x)  # Mask for the middle segment
        mask2 = (1 << GeneticAlgorithm.BIT_LENGTH) - 1  # Mask for all bits
        left_mask = mask2 ^ ((1 << point_y) - 1)  # Mask for the left segment
        right_mask = (1 << point_x) - 1  # Mask for the right segment

        parent1 = parent1.genome
        parent2 = parent2.genome

        # Extract segments
        middle1 = parent1 & mask1
        middle2 = parent2 & mask1
        left1 = parent1 & left_mask
        right1 = parent1 & right_mask
        left2 = parent2 & left_mask
        right2 = parent2 & right_mask
        # mDNA is the same for both offspring
        mDNA = parent1 & 0x7F

        # Form new offspring
        child1 = left1 | middle2 | right1 | mDNA
        child2 = left2 | middle1 | right2 | mDNA

        return child1, child2

    def mutate(self, individual):
        # Implement mutation logic - Bit-flip mutation
        # Give each bit a (1/bit_length) * mutation_rate chance of flipping
        mutation_mask = 0
        for i in range(GeneticAlgorithm.BIT_LENGTH):
            if np.random.rand() < (self.mutation_rate/GeneticAlgorithm.BIT_LENGTH):
                mutation_mask |= 1 << i
        
        return individual ^ mutation_mask

    def evaluate_fitness(self):
        # Each strategy plays a tournament against every other strategy
        # The fitness is the sum of the scores against each opponent
        for i in range(self.population_size):
            for j in range(i + 1, self.population_size):
                # Play a game between strategy i and strategy j
                self.prisoner_dilemma(self.population[i], self.population[j])

    def evaluate_fitness_test(self):
        # Each strategy plays a tournament against every other strategy
        # The fitness is the sum of the scores against each opponent
        for i in range(self.population_size):
            self.population[i].fitness = count_different_bits(0xcafedeadbeefbabe,self.population[i].genome)
    
    
    def prisoner_dilemma(self, strategy1, strategy2):
        strategy1.name = 'strategy_one'
        strategy2.name = 'strategy_two'
        test_history = memory.Memory()
        for k in range(200):
            decision_one = strategy1.make_decision(test_history)
            decision_two = strategy2.make_decision(test_history)

            test_history.update_memory(strategy1.name, decision_one[0])
            test_history.update_memory(strategy2.name, decision_two[0])
        strategy1_score, strategy2_score = test_history.score()
        strategy1.fitness += strategy1_score
        strategy2.fitness += strategy2_score
    
    def run_generation(self, print_output=False):
        # Run a generation: evaluate, select, crossover, mutate
        self.evaluate_fitness()
        self.population.sort(reverse=True, key=lambda x: x.fitness)
        if print_output:
            print(f"Fitness: {self.population[0].fitness}")
            print(f"Genome: {hex(self.population[0].genome)}")
            #print(f"Best strategy: {self.population[0].behavior}")
            print(f"Avg fitness: {np.mean([x.fitness for x in self.population])}")
        new_population = []
        for _ in range(self.population_size // 2):
            parent1, parent2 = self.select()
            if np.random.rand() < self.crossover_rate:
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                new_population.append(Strategy(child1))
                new_population.append(Strategy(child2))
            else:
                new_population.append(Strategy(parent1.genome))
                new_population.append(Strategy(parent2.genome))
        self.population = new_population


def main():
    ga = GeneticAlgorithm(1000, 0.14, 0.8)
    # Run the genetic algorithm for a certain number of generations
    for i in range(1000):
        ga.run_generation((i % 100 == 0))
    # Stop timing
    


if __name__ == "__main__":
    main()
