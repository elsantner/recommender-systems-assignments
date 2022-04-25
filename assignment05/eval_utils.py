import math


# calculate Mean Absolute Error (MAE)
# rating_predictions ... list of dictionaries containing 'prediction' and 'actual' keys
def mae(rating_predictions):
    sum_of_abs_diff = 0
    for entry in rating_predictions:
        sum_of_abs_diff += abs(entry['prediction'] - entry['actual'])

    return sum_of_abs_diff / len(rating_predictions)


# calculate Root Mean Square Error (RMSE)
# rating_predictions ... list of dictionaries containing 'prediction' and 'actual' keys
def rmse(rating_predictions):
    sum_of_squared_diff = 0
    for entry in rating_predictions:
        sum_of_squared_diff += pow(entry['prediction'] - entry['actual'], 2)

    return math.sqrt(sum_of_squared_diff)
