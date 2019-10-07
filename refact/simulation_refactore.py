# Simulate evolution in a sequence with overlapping reading frames according to the new data structure from new_sequence_info.py
import numpy as np
import random
from new_sequence_info import Sequence


class Simulate:
    """
    Simulate evolution within a sequence throughout a phylogeny
    :ivar seq: list of nucleotides. Each nucleotide stores information about their reading frames and evolutionary rates
    :ivar tree: rooted phylogenetic tree over which seq evolves
    """

    def __init__(self, sequence , phylo_tree = None):
        self.sequence  = sequence # Object of class Sequence (Double Linked list of Nucleotides)
        self.phylo_tree = phylo_tree
        self.event_tree = self.sequence.event_tree # Tree of class EventTree (all possible mutations related to sequence)


    def get_substitution(self):
        """
        Select a substitution by moving over the event_tree according to the generation of random numbers
        """
        # Select: to nucleotide
        print("Entering get substitution")
        events = self.event_tree['total_events']
        to_mutation = self.select_weighted_values(self.event_tree['to_nt'], events, 'events_for_nt', 'stationary_frequency')

        # Select: possible from nucleotides
        from_dict = self.event_tree['to_nt'][to_mutation]['from_nt']
        events_for_nt = self.event_tree['to_nt'][to_mutation]['events_for_nt']
        from_mutation = self.select_weighted_values(from_dict, events_for_nt, 'number_of_events', 'kappa')
        final_mutation = self.event_tree['to_nt'][to_mutation]['from_nt'][from_mutation]

        # List of nucleotides that are candidates to mutate
        candidate_nts = final_mutation['nts_in_subs']
        rates_list = [nt.mutation_rate for nt in candidate_nts]
        nt_dict = dict(zip(candidate_nts, rates_list))

        # Select weighted nucleotide
        from_nucleotide = self.weighted_random_choice(nt_dict, sum(rates_list))

        return from_nucleotide, to_mutation

    def select_weighted_values(self, dictionary, number_of_total_events, key_for_local_events, key_to_weight):
        """
        Randomly selected a key from a dictionary of events with weighted values
        :param number_of_total_events: Number of total number of events on branch
        :param number_of_local_events: key to the number of events for each specific value
        :param key_to_weight: Depending on the level of the branch, this could be:
                - the key to stationary frequency
                - the key to transition/transversion rate ratio
        """

        total_events = number_of_total_events
        temp = {}
        sum_values = 0
        # Create a temp dictionary to store the weighted values
        for key, value in dictionary.items():
            if value:
                # weight values
                temp[key] = (value[key_for_local_events]/total_events)*value[key_to_weight]
                sum_values += temp[key]
            else:
                temp[key] = None

        # Randomly selected a key on the dictionary
        return self.weighted_random_choice(temp, sum_values)

    @staticmethod
    def weighted_random_choice(dictionary, sum_values):
        """
        Randomly select a key on a dictionary where values correspond to the weight for the key
        :param dictionary: Dictionary to select the value from
        :param sum_values: sum all values on dict to establish the limit for the mutation
        :return: random key from dict
        """

        iter_object = iter(dictionary.items())
        limit = random.uniform(0, sum_values)
        s = 0
        while s < limit:
            try:
                (key, value) = next(iter_object)
                if value:
                    s += value
                else:
                    pass
            except StopIteration:
                break

        return key

    def sum_rates(self):
        """
        Calculate the total mutation rate of sequence
        """
        total_rate = sum([nt.mutation_rate for nt in iter(self.sequence.nt_sequence)])
        return total_rate

    def draw_waiting_time(self, instant_rate):
        """
        Draw a time at which mutation occurs according to mutation rates.
        :return:
        """
        time = np.random.exponential(scale=instant_rate)
        return time

    def mutate_on_branch(self, branch_length):
        """
        Simulate molecular evolution in sequence given a branch length
        """

        times_sum = 0
        instant_rate = self.sum_rates()

        while True:
            #print("ENTERING MUTATE ON BRANCH")
            random_time = self.draw_waiting_time(instant_rate)
            times_sum += random_time
            #print("Random time: ",random_time)
            #print("Instant_rate", instant_rate)

            if times_sum > branch_length:
                break

            # Draw a mutation
            mutation = self.get_substitution()
            my_nt = mutation[0]
            to_state = mutation[1]

            # Remove the mutated nucleotide from the event tree and update information in Nucleotide
            self.remove_nt(my_nt)
            self.update_nucleotide(my_nt, to_state)


            # adjacent_positions = [my_nt.pos_in_seq-2, my_nt.pos_in_seq-1, my_nt.pos_in_seq+1, my_nt.pos_in_seq+2]
            # for i in adjacent_positions:
            #     adj_nt = self.sequence.nucleotide_at_position(i)


            # TODO: update parameters for adjacent nucleotides

    def remove_nt(self, nt):
        """
        Find nucleotide selected to mutate in the event tree and remove it from every branch on the event tree
        :param nt:
        :return:
        """
        for key_to_nt, value_to_nt in self.event_tree['to_nt'].items():
            if key_to_nt != nt.state:
                # Find branches that contain my nucleotide
                my_branch = self.event_tree['to_nt'][key_to_nt]['from_nt'][nt.state]
                 # Remove nt from non-synonymous mutations
                for omega_key, nucleotide_list in my_branch['is_nonsyn'].items():
                    if nt in nucleotide_list:
                        nucleotide_list.remove(nt)
                # Remove nt from synonymous mutations and list of nucleotides in substitution
                if nt in my_branch['is_syn']: my_branch['is_syn'].remove(nt)
                if nt in my_branch['nts_in_subs']: my_branch['nts_in_subs'].remove(nt)

    def update_nucleotide(self, nt, to_state):
        """
        Update parameters on the mutated nucleotide
        """

        # Update the state of the nucleotide
        nt.set_state(to_state)
        # Update rates, omega key and event tree with the nucleotide according to its new state
        nt.set_complement_state()  # Change complementary state given the mutation
        rates = self.sequence.get_substitution_rates(nt)  # Calculate new rates and update event tree
        nt.set_rates(rates[0])  # Update substitution rates
        nt.set_my_omegas(rates[1]) # Update omega keys
        nt.set_nt_rate()