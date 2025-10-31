def one_rep_max(weight: float, reps: int) -> float:
    """Estimate 1RM using Brzycki formula"""
    if reps >= 37:
        raise ValueError("Reps must be less than 37 for this formula")
    elif weight <=0:
        raise ValueError("weight should not be less than 0")

    return weight * (36 / (37 - reps))
    
    