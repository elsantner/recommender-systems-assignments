# create empty list for ratings
ratings = []

f = open('resources/ratings.csv', 'r')
# skip first line (i.e. headers)
ratingsIter = iter(f)
next(ratingsIter)
for line in ratingsIter:
    ratings.append(float(line.split(',')[2]))

rating_sum = 0
for r in ratings:
    rating_sum += r

print('Mean rating: {0}'.format(rating_sum / len(ratings)))