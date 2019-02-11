# Calculate evolution rates across the sequence

# The substitution rate matrix
transition_score = -5
transversion_score = -1
synonymous_score = 5
nonsynonymous_score = 1
rate_matrix = {
    'A': {
        'A': 0,
        'C': transversion_score,
        'T': transversion_score,
        'G': transition_score,
    },

}

def get_frequency_rates(seq):
    frequencies = {
        'A': 0,
        'C': 0,
        'T': 0,
        'G': 0,
    }

    for nucleotide in seq:
        frequencies[nucleotide] =+ 1

    return { nucleotide: ocurrences/len(seq) for nucleotide, ocurrences in frequencies.items() }


def get_syn_nonsyn_score():
    return 1


def get_tt_score(current, mutated):
    return 1


def evol_rates(seq):
    mutation_rates = []
    # Step 1: Calculate frequency rate of nucleotides
    frequency_rates = get_frequency_rates(seq)

    # Step 2: Calculate mutation rate for each nucleotide in the sequence
    for nucleotide in seq:
        mutated = 'A' # TODO: How do I select this?
        mutation_rates.append({
            nucleotide: frequency_rates[nucleotide] * get_tt_score(nucleotide, mutated) * get_syn_nonsyn_score()
        })


    # Map of nucleotides with their respective mutation rate
    return mutation_rates

    # A A A A A A


    # Position nucleotide mutation_rate
    # 1            A          0.2
    # 2
    # .
    # .

if __name__ == '__main__':
    print(evol_rates(('A', 'T', 'G', 'C', 'A', 'A', 'A')))
