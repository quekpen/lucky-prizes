from typing import Sequence

import numpy as np

import tkinter as tk
from tkinter import simpledialog

import seaborn as sns
import matplotlib.pyplot as plt


def calculate_p_parameters(
    prize_vals: Sequence(int), num_prizes: Sequence(int), prize_ratio: int
) -> Sequence(float):
    """
    Given publicly available information around expected prize distribution,
    calculate the full set of probability parameters required to simulate the
    relevant multinomial distribution.
    """
    total_prizes = sum(num_prizes) * prize_ratio

    # Append the number of prizes with the number of Premium Bonds that will not win in a given month.
    num_prizes.append(total_prizes - sum(num_prizes))

    # These probabilities are used as parameters in the multinomial distribution simulations below.
    return [n / sum(num_prizes) for n in num_prizes]


def simulate_winnings(
    num_bonds: int,
    pvals: Sequence(float),
    prize_vals: Sequence(int),
    num_sims: int,
):
    """
    Simulates the number of prizes won for the given number of Premium Bonds in a month.
    """
    rng = np.random.default_rng()
    sims = rng.multinomial(num_bonds, pvals, size=(num_sims, 12))
    # Calculate the total cash winnings given the number of prizes (of various sizes) won.
    yearly_winnings = []
    for sim in sims:
        monthly_winnings = []
        for month in sim:
            prize = sum([v * s for v, s in zip(prize_vals, month)])
            monthly_winnings.append(prize)
        yearly_winnings.append(sum(monthly_winnings))
    return yearly_winnings


def return_effective_rate(yearly_winnings: Sequence(int), num_bonds: int):
    """
    Returns the results of the simulations in the form of a histogram showing
    the distribution of returns, as well as the median winnings and rate.
    """
    sns.set(rc={"figure.figsize": (10, 5)})
    ax = sns.histplot(
        data=[i for i in yearly_winnings if i < num_bonds]
    )  # Truncate distribution so chart is informative.
    plt.axvline(np.median(yearly_winnings), color="red")
    plt.xlabel("Annual winnings")
    plt.ylabel("Number of simulations")
    interval = round(np.percentile(yearly_winnings, 10), 0), round(
        np.percentile(yearly_winnings, 90), 0
    )
    plt.axvline(interval[0], color="lightgray", linestyle="-.")
    plt.axvline(interval[1], color="lightgray", linestyle="-.")
    median_winnings = np.median(yearly_winnings)
    median_rate = np.median(yearly_winnings) / num_bonds
    ax.text(0.25, 0.8, f"Investment: £{int(num_bonds)}", transform=ax.transAxes)
    ax.text(
        0.25,
        0.7,
        f"Median annual winnings: £{int(median_winnings)}",
        transform=ax.transAxes,
    )
    ax.text(
        0.25, 0.6, f"Median annual rate: {median_rate * 100}%", transform=ax.transAxes
    )
    ax.text(
        0.25,
        0.5,
        f"You have an 80% chance of winning between £{int(interval[0])} and £{int(interval[1])}",
        transform=ax.transAxes,
    )
    plt.show()


def main():
    # These values come from the August NS&I announcement (see README for additional details).
    # As a result, the results will correspond to winnings from September 2023 onwards, assuming
    # rates stay as they are.
    prize_vals = [
        1_000_000,
        100_000,
        50_000,
        25_000,
        10_000,
        5_000,
        1_000,
        500,
        100,
        50,
        25,
        0,
    ]
    num_prizes = [
        2,
        90,
        181,
        360,
        902,
        1_803,
        18_832,
        56_496,
        2_339_817,
        2_339_817,
        1_027_604,
    ]
    prize_ratio = 21_000

    pvals = calculate_p_parameters(prize_vals, num_prizes, prize_ratio)

    # Open the input dialog for the user to specify the number of Premium Bonds they would like to calculate the effective rate for.
    # This is one of the necessary parameters to calculate the effective rate.
    ROOT = tk.Tk()
    ROOT.withdraw()
    num_bonds = simpledialog.askinteger(
        title="", prompt="How many Premium Bonds have you bought?"
    )

    yearly_winnings = simulate_winnings(num_bonds, pvals, prize_vals)

    return_effective_rate(yearly_winnings, num_bonds)


if __name__ == "__main__":
    main()
