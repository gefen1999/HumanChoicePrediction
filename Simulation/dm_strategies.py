import numpy as np
import json

################################
# CONSTS
################################

REVIEWS = 0
BOT_ACTION = 1
USER_DECISION = 2


################################
def calculate_disappointment(previous_rounds):
    """
    Calculates the level of disappointment for each round based on user decisions and review averages.
    A round is marked as disappointing (1) if the average review is below 8 and the user decided to continue,
    or if the average review is 8 or above and the user decided not to continue. Otherwise, it's not disappointing (0).

    Args:
        previous_rounds (list of dicts): Each dict contains 'REVIEWS' and 'USER_DECISION' for a round.

    Returns:
        dict: A dictionary with round numbers as keys and disappointment indicators (0 or 1) as values.
    """
    disappointment = {}
    for i, r in enumerate(previous_rounds):
        if sum(r[0]) / len(r[0]) < 8 and r[2] == 1:
            disappointment[i] = 1
        elif sum(r[0]) / len(r[0]) >= 8 and r[2] == 0:
            disappointment[i] = 1
        else:
            disappointment[i] = 0
    return disappointment


def conservative_strategy(information, config):
    """
    A conservative approach to decision making that aims to minimize disappointment.
    Decisions are based on a threshold of disappointment ratio; if the ratio is below
    a certain threshold, indicating lower disappointment, the strategy decides to continue (1).
    This threshold adjusts based on the number of rounds played.
    """

    disappointment_counter = sum(calculate_disappointment(information["previous_rounds"]).values())
    len_previous_rounds = len(information["previous_rounds"])
    if len_previous_rounds == 0:  # rely on bot message for first round
        return 1 if information["bot_message"] >= 8 else 0

    initial_threshold = config["conservative_strategy_initial_threshold"]
    # decreasing initial_threshold will make the strategy more conservative
    alpha = config["conservative_strategy_alpha"]
    # increasing alpha will make the strategy more conservative
    threshold = initial_threshold - alpha * len_previous_rounds
    min_threshold = config["conservative_strategy_min_threshold"]
    # decreasing min_threshold will make the strategy more conservative
    threshold = max(threshold, min_threshold)

    if disappointment_counter / len_previous_rounds < threshold:
        return 1
    else:
        return 0


def aggressive_pursuit(information, config):
    """
    An aggressive (optimistic) strategy that opts to continue (1 - go to hotel) despite higher levels of disappointment,
    betting on a change in trend. It uses a fixed interval approach where, after a certain number
    of disappointing outcomes, it decides to continue. The interval adjusts more dynamically based on the number
    of rounds played, aiming to be responsive to the user's journey through quicker adaptation.
    """
    disappointment_counter = sum(calculate_disappointment(information["previous_rounds"]).values())
    len_previous_rounds = len(information["previous_rounds"])
    if len_previous_rounds == 0:  # rely on bot message for first round
        return 1 if information["bot_message"] >= 8 else 0

    fixed_interval = config["aggressive_pursuit_fixed_interval"]
    # Increasing the fixed_interval will make the strategy more aggressive
    divisor = config["aggressive_pursuit_divisor"]
    # decreasing the divisor will make the strategy more aggressive

    interval_adjustment = (len_previous_rounds // divisor)  # Adjustment occurs more frequently and increases over time.

    if disappointment_counter < (fixed_interval + interval_adjustment):
        return 1
    else:
        return 0


def adaptive_learning(information, config):
    """
    Adjusts decisions dynamically based on the trend of recent disappointments and the overall disappointment ratio.
    It considers the user's total experience, aiming to reduce future disappointment by learning from the past.
    The strategy uses the recent trend of disappointment (last 3 rounds) and the overall disappointment ratio
    to decide whether to continue (1) or not (0). It emphasizes minimizing disappointment in future rounds.
    """

    disappointment_dict = calculate_disappointment(information["previous_rounds"])
    disappointment_counter = sum(disappointment_dict.values())
    len_previous_rounds = len(information["previous_rounds"])

    if len_previous_rounds < 3:  # rely on bot message for first 3 rounds
        return 1 if information["bot_message"] >= 8 else 0

    disappointment_ratio = disappointment_counter / len_previous_rounds
    recent_disappointment = [disappointment_dict.get(len_previous_rounds - 3 + i, 0) for i in range(3)]
    recent_disappointment_ratio = sum(recent_disappointment) / len(recent_disappointment)

    disappointment_threshold = config["adaptive_learning_disappointment_threshold"]
    # decreasing the disappointment_threshold will make the strategy more conservative

    # Decision making based on recent and overall disappointment ratios
    if disappointment_ratio < disappointment_threshold and recent_disappointment_ratio < disappointment_threshold:
        return 1  # Continue if both overall and recent disappointments are manageable
    elif recent_disappointment_ratio == 1:
        return 0  # Discontinue if the last 3 rounds were all disappointing
    else:
        # In ambiguous cases, consider the trend of recent disappointments
        if recent_disappointment[-1] == 0 and sum(recent_disappointment) <= 1:
            return 1  # Continue if the most recent round was not disappointing and at least 2 of the last 3 rounds were not disappointing
        else:
            return 0  # Otherwise, discontinue


def correct_action(information, **kwargs):
    if information["hotel_value"] >= 8:
        return 1
    else:
        return 0


def random_action(information, **kwargs):
    return np.random.randint(2)


def user_rational_action(information, **kwargs):
    if information["bot_message"] >= 8:
        return 1
    else:
        return 0


def user_picky(information, **kwargs):
    if information["bot_message"] >= 9:
        return 1
    else:
        return 0


def user_sloppy(information, **kwargs):
    if information["bot_message"] >= 7:
        return 1
    else:
        return 0


def user_short_t4t(information, **kwargs):
    if len(information["previous_rounds"]) == 0 \
            or (information["previous_rounds"][-1][BOT_ACTION] >= 8 and
                information["previous_rounds"][-1][REVIEWS].mean() >= 8) \
            or (information["previous_rounds"][-1][BOT_ACTION] < 8 and
                information["previous_rounds"][-1][REVIEWS].mean() < 8):  # cooperation
        if information["bot_message"] >= 8:  # good hotel
            return 1
        else:
            return 0
    else:
        return 0


def user_picky_short_t4t(information, **kwargs):
    if information["bot_message"] >= 9 or ((information["bot_message"] >= 8) and (
            len(information["previous_rounds"]) == 0 or (
            information["previous_rounds"][-1][REVIEWS].mean() >= 8))):  # good hotel
        return 1
    else:
        return 0


def user_hard_t4t(information, **kwargs):
    if len(information["previous_rounds"]) == 0 \
            or np.min(np.array([((r[BOT_ACTION] >= 8 and r[REVIEWS].mean() >= 8)
                                 or (r[BOT_ACTION] <= 8 and r[REVIEWS].mean() < 8)) for r in
                                information["previous_rounds"]])) == 1:  # cooperation
        if information["bot_message"] >= 8:  # good hotel
            return 1
        else:
            return 0
    else:
        return 0


def history_and_review_quality(history_window, quality_threshold):
    def func(information, **kwargs):
        if len(information["previous_rounds"]) == 0 \
                or history_window == 0 \
                or np.min(np.array([((r[BOT_ACTION] >= 8 and r[REVIEWS].mean() >= 8)
                                     or (r[BOT_ACTION] <= 8 and r[REVIEWS].mean() < 8)) for r in
                                    information["previous_rounds"][
                                    -history_window:]])) == 1:  # cooperation from *result's* perspective
            if information["bot_message"] >= quality_threshold:  # good hotel from user's perspective
                return 1
            else:
                return 0
        else:
            return 0
    return func


def topic_based(positive_topics, negative_topics, quality_threshold):
    def func(information, **kwargs):
        review_personal_score = information["bot_message"]
        for rank, topic in enumerate(positive_topics):
            review_personal_score += int(information["review_features"].loc[topic])*2/(rank+1)
        for rank, topic in enumerate(negative_topics):
            review_personal_score -= int(information["review_features"].loc[topic])*2/(rank+1)
        if review_personal_score >= quality_threshold:  # good hotel from user's perspective
            return 1
        else:
            return 0
    return func


def LLM_based(is_stochastic):
    with open(f"data/baseline_proba2go.txt", 'r') as file:
        proba2go = json.load(file)
        proba2go = {int(k): v for k, v in proba2go.items()}

    if is_stochastic:
        def func(information, **kwargs):
            review_llm_score = proba2go[information["review_id"]]
            return int(np.random.rand() <= review_llm_score)
        return func
    else:
        def func(information, **kwargs):
            review_llm_score = proba2go[information["review_id"]]
            return int(review_llm_score >= 0.5)
        return func