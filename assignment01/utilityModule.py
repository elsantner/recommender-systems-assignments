class Statistics:
    def __init__(self, filename):
        self.filename = filename

    def computeRatingStats(self):
        try:
            # create empty list for ratings
            ratings = []

            f = open(self.filename, 'r')
            # skip first line (i.e. headers)
            ratingsIter = iter(f)
            next(ratingsIter)
            for line in ratingsIter:
                ratings.append(float(line.split(',')[2]))

            rating_sum = 0
            for r in ratings:
                rating_sum += r

            # return mean, median and mode
            return rating_sum / len(ratings)

        except FileNotFoundError as err:
            raise Exception('File "{0}" could not be found'.format(err.filename))
        except StopIteration:
            raise Exception('No read access to file')
        except ValueError:
            raise Exception('Cannot parse input - rating has invalid format')
