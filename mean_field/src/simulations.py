"""
Source code for simulations

Author: Matthew DeVerna
"""
import numpy as np


def get_peak_day(infected_array):
    """
    Return the day on which the highest level of infection occurred.
    Function finds the max value, returns the index of that value, and adds 1.
    """
    return np.where(np.array(infected_array) == max(infected_array))[0][0] + 1


def deriv_simple(beta_o, beta_m, sus_o, sus_m, inf_o, inf_m, k, counts=False, N=None):
    """
    Calculate the *change* in population for all six compartments in the scenario
    where we consider two populations — ordinary and misinformed — (and thus six
    compartments), but no homophily.

    Parameters:
    -----------
    - beta_o (float) : proportion of population infected (ordinary)
    - beta_m (float) : proportion of the population infected (misinformed)
    - sus_o (float) : proportion of the population susceptible (ordinary)
    - sus_m (float) : proportion of the population susceptible (misinformed)
    - inf_o (float) : proportion of the population infected (ordinary)
    - inf_m (float) : proportion of the population infected (misinformed)
    - k (inf)       : the rate of recovery (i.e., 1 / num days to recover)
    - counts (bool) : if True, run the simulation based on a number of people
    - N (int)       : size of the population to run with `counts`

    Returns
    -----------
    The *change* in the population for...
    - ds_o : susceptible (ordinary)
    - di_o : infected (ordinary)
    - dr_o : recovered (ordinary)
    - ds_m : susceptible (misinformed)
    - di_m : infected (misinformed)
    - dr_m : recovered (misinformed)
    """
    if not counts:
        # Ordinary folks first
        ds_o = -beta_o * sus_o * (inf_o + inf_m)
        di_o = (beta_o * sus_o * (inf_o + inf_m)) - k * inf_o
        dr_o = k * inf_o

        # Misinfo folks next
        ds_m = -beta_m * sus_m * (inf_o + inf_m)
        di_m = (beta_m * sus_m * (inf_o + inf_m)) - k * inf_m
        dr_m = k * inf_m

    else:
        if N is None:
            raise ValueError("`N` must be set with `counts = True`")

        # Ordinary folks first
        ds_o = (-beta_o * sus_o * (inf_o + inf_m)) / N
        di_o = (((beta_o * sus_o * (inf_o + inf_m))) / N) - k * inf_o
        dr_o = k * inf_o

        # Misinfo folks next
        ds_m = (-beta_m * sus_m * (inf_o + inf_m)) / N
        di_m = (((beta_m * sus_m * (inf_o + inf_m))) / N) - k * inf_m
        dr_m = k * inf_m

    return ds_o, di_o, dr_o, ds_m, di_m, dr_m


def deriv_with_homophily(
    beta_o, beta_m, sus_o, sus_m, inf_o, inf_m, k, alpha, counts=False, N=None
):
    """
    Calculate the *change* in population for all six compartments in the scenario
    where we consider two populations — ordinary and misinformed — (and thus six
    compartments), also accounting for homophily.

    Parameters:
    -----------
    - beta_o (float) : proportion of population infected (ordinary)
    - beta_m (float) : proportion of the population infected (misinformed)
    - sus_o (float)  : proportion of the population susceptible (ordinary)
    - sus_m (float)  : proportion of the population susceptible (misinformed)
    - inf_o (float)  : proportion of the population infected (ordinary)
    - inf_m (float)  : proportion of the population infected (misinformed)
    - k (inf)        : the rate of recovery (i.e., 1 / num days to recover)
    - alpha (float)  : level of homophily. Must fall in range: .5 <= alpha <= 1
    - counts (bool)  : if True, run the simulation based on a number of people
    - N (int)        : size of the population to run with `counts`

    Returns
    -----------
    The *change* in the population for...
    - ds_o : susceptible (ordinary)
    - di_o : infected (ordinary)
    - dr_o : recovered (ordinary)
    - ds_m : susceptible (misinformed)
    - di_m : infected (misinformed)
    - dr_m : recovered (misinformed)
    """
    if not (0.5 <= np.round(alpha, 2) <= 1):
        raise ValueError(f"`alpha` must fall in the range [.5,1]. Alpha = {alpha}")

    if not counts:
        # Ordinary folks first
        ds_o = -2 * beta_o * sus_o * (inf_o * alpha + inf_m * (1 - alpha))
        di_o = 2 * beta_o * sus_o * (inf_o * alpha + inf_m * (1 - alpha)) - k * inf_o
        dr_o = k * inf_o

        # Misinfo folks next
        ds_m = -2 * beta_m * sus_m * (inf_o * (1 - alpha) + inf_m * alpha)
        di_m = 2 * beta_m * sus_m * (inf_o * (1 - alpha) + inf_m * alpha) - k * inf_m
        dr_m = k * inf_m

    else:
        if N is None:
            raise ValueError("`N` must be set with `counts = True`")

        # Ordinary folks first
        ds_o = -2 * beta_o * sus_o * (inf_o * alpha + inf_m * (1 - alpha)) / N
        di_o = (
            (2 * beta_o * sus_o * (inf_o * alpha + inf_m * (1 - alpha))) / N
        ) - k * inf_o
        dr_o = k * inf_o

        # Misinfo folks next
        ds_m = (-2 * beta_m * sus_m * (inf_o * (1 - alpha) + inf_m * alpha)) / N
        di_m = (
            (2 * beta_m * sus_m * (inf_o * (1 - alpha) + inf_m * alpha)) / N
        ) - k * inf_m
        dr_m = k * inf_m

    return ds_o, di_o, dr_o, ds_m, di_m, dr_m


def run_simulation(
    frac_ord,
    prop_infec,
    num_days,
    beta_ord,
    recovery_days,
    beta_mult,
    w_homophily,
    alpha,
    mixed=False,
    counts=False,
    N=None,
):
    """
    Run an SIR simulation for the indicated number of days based on the
    provided parameters.

    Parameters:
    -----------
    - frac_ord (float) : the proportion of the population made up of "ordinary"
        individuals. frac_misinformed is 1 - frac_ord
    - prop_infec (float) : the proportion of the population that is initialized
        as infected. This is a subgroup of the misinformed individuals
    - num_days (int) : the number of days to run the simulation for
    - beta_ord (float) : the probability of disease transmission for the ordinary
        individuals.
    - recovery_days (int) : the number of days it takes for individuals to recover
    - beta_mult (float/int) : how much to multiple beta_ord by to get beta_misinfo
    - w_homophily (bool) : if True, use `deriv_with_homophily`. Else, use `deriv_simple`
    - alpha (float)  : level of homophily. Must fall in range: .5 <= alpha <= 1
    - mixed (bool)   : whether to mix initially infected between both the misinformed and ordinary
    - counts (bool)  : if True, run the simulation based on a number of people
    - N (int)        : size of the population to run with `counts`
    """

    eps = prop_infec
    x = frac_ord

    step_size = 1  # step size
    all_steps = np.arange(0, num_days, step_size)

    ### Set initial values ###
    S_o = np.zeros(len(all_steps))
    S_m = np.zeros(len(all_steps))
    I_o = np.zeros(len(all_steps))
    I_m = np.zeros(len(all_steps))
    R_o = np.zeros(len(all_steps))
    R_m = np.zeros(len(all_steps))

    ### Set up the initial conditions
    # If mixed, infect both groups equally
    if mixed:
        S_o[0] = x - (eps / 2)
        S_m[0] = 1 - x - (eps / 2)
        I_o[0] = eps / 2
        I_m[0] = eps / 2

    # Otherwise we only infect one group
    else:
        # If we only have ordinary folks, we must infect the ordinary group
        if x == 1:
            S_o[0] = x - eps
            I_o[0] = eps

        # Otherwise, we infect the misinformed group
        else:
            S_o[0] = x
            S_m[0] = 1 - x - eps
            I_m[0] = eps

    # Set recovery rate
    k = 1 / recovery_days

    # Setting beta values
    B_o = beta_ord
    B_m = B_o * beta_mult
    # B_m = 1 if B_m >= 1 else B_m

    # Get r0 values
    ord_r0 = B_o / k
    mis_r0 = B_m / k
    weighted_avg_r0 = np.average([ord_r0, mis_r0], weights=[x, 1 - x])

    r0s = (ord_r0, mis_r0, weighted_avg_r0)

    for t in range(0, len(all_steps) - 1):
        # Calculate the change of each value
        if w_homophily:
            d_s_o, d_i_o, d_r_o, d_s_m, d_i_m, d_r_m = deriv_with_homophily(
                beta_o=B_o,
                beta_m=B_m,
                sus_o=S_o[t],
                sus_m=S_m[t],
                inf_o=I_o[t],
                inf_m=I_m[t],
                k=k,
                alpha=alpha,
                counts=counts,
                N=N,
            )
        else:
            d_s_o, d_i_o, d_r_o, d_s_m, d_i_m, d_r_m = deriv_simple(
                beta_o=B_o,
                beta_m=B_m,
                sus_o=S_o[t],
                sus_m=S_m[t],
                inf_o=I_o[t],
                inf_m=I_m[t],
                k=k,
                counts=counts,
                N=N,
            )

        # Ensure that the total change is zero because individuals should
        # simply be shifting between compartments
        total_change = d_s_o + d_s_m + d_i_o + d_i_m + d_r_o + d_r_m
        assert np.allclose(total_change, 0), f"{total_change}"

        # Set the next value as the current plus it's change
        S_o[t + 1] = S_o[t] + d_s_o
        S_m[t + 1] = S_m[t] + d_s_m
        I_o[t + 1] = I_o[t] + d_i_o
        I_m[t + 1] = I_m[t] + d_i_m
        R_o[t + 1] = R_o[t] + d_r_o
        R_m[t + 1] = R_m[t] + d_r_m

    return S_o, S_m, I_o, I_m, R_o, R_m, r0s
