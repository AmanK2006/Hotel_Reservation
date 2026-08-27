from scipy.stats import randint, uniform


PARAM_DIST = {
    "n_estimators" : randint(100, 500),
    "max_samples" : uniform(0.7, 0.9),
    "learning_rate" : uniform(0.01, 0.2),
    "boosting" : ["gbdt", "rf", "dart"],
    "num_leaves" : randint(10, 30),
    "max_depth" : randint(5, 20)
}

RANDOM_SEARCH = {
    "scoring": "accuracy",
    "n_iter": 5,          # Keep iterations low (5 * 5 = 25 fits) for fast CI builds
    "n_jobs": 1,          # CRITICAL: Prevent CPU deadlocks inside Docker/Jenkins
    "verbose": 1,
    "cv": 5,
    "random_state": 42
}

__all__ = [
    "PARAM_DIST",
    "RANDOM_SEARCH"
    ]