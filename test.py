from __future__ import print_function
import numpy as np
conn = np.loadtxt("ranked_vectors/ConnectivityVector.csv", delimiter=",", skiprows=1)
conn = conn.T
import numpy as np
from itertools import combinations, permutations

def kendalltau_dist(rank_a, rank_b):
    tau = 0
    n_candidates = len(rank_a)
    for i, j in combinations(range(n_candidates), 2):
        tau += (np.sign(rank_a[i] - rank_a[j]) ==
                -np.sign(rank_b[i] - rank_b[j]))
    return tau
def _build_graph(ranks):
    n_voters, n_candidates = ranks.shape
    edge_weights = np.zeros((n_candidates, n_candidates))
    for i, j in combinations(range(n_candidates), 2):
        preference = ranks[:, i] - ranks[:, j]
        h_ij = np.sum(preference < 0)  # prefers i to j
        h_ji = np.sum(preference > 0)  # prefers j to i
        if h_ij > h_ji:
            edge_weights[i, j] = h_ij - h_ji
        elif h_ij < h_ji:
            edge_weights[j, i] = h_ji - h_ij
    return edge_weights

print(_build_graph(conn))

from lp_solve import lp_solve 

def rankaggr_lp(ranks):
    """Kemeny-Young optimal rank aggregation"""

    n_voters, n_candidates = ranks.shape
    
    # maximize c.T * x
    edge_weights = _build_graph(ranks)
    c = -1 * edge_weights.ravel()  

    idx = lambda i, j: n_candidates * i + j

    # constraints for every pair
    pairwise_constraints = np.zeros(((n_candidates * (n_candidates - 1)) / 2,
                                     n_candidates ** 2))
    for row, (i, j) in zip(pairwise_constraints,
                           combinations(range(n_candidates), 2)):
        row[[idx(i, j), idx(j, i)]] = 1

    # and for every cycle of length 3
    triangle_constraints = np.zeros(((n_candidates * (n_candidates - 1) *
                                     (n_candidates - 2)),
                                     n_candidates ** 2))
    for row, (i, j, k) in zip(triangle_constraints,
                              permutations(range(n_candidates), 3)):
        row[[idx(i, j), idx(j, k), idx(k, i)]] = 1

    constraints = np.vstack([pairwise_constraints, triangle_constraints])
    constraint_rhs = np.hstack([np.ones(len(pairwise_constraints)),
                                np.ones(len(triangle_constraints))])
    constraint_signs = np.hstack([np.zeros(len(pairwise_constraints)),  # ==
                                  np.ones(len(triangle_constraints))])  # >=

    obj, x, duals = lp_solve(c, constraints, constraint_rhs, constraint_signs,
                             xint=range(1, 1 + n_candidates ** 2))

    x = np.array(x).reshape((n_candidates, n_candidates))
    aggr_rank = x.sum(axis=1)

    return obj, aggr_rank

rankaggr_lp(_build_graph(conn))
