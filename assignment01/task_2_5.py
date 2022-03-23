import utilityModule

statistics = utilityModule.Statistics('resources/ratings.csv')
stats = statistics.computeRatingStats()
print('Mean: {0}'.format(stats))
