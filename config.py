from enum import Enum


class MatchingAlgorithm(Enum):
    BEST_OF_FIVE_LOWEST_INTEREST = 1


class Config(Enum):
    MIN_BIDS_EXPECTED = 5
    SELECTED_MATCHING_ALGORITHM = MatchingAlgorithm.BEST_OF_FIVE_LOWEST_INTEREST.value
