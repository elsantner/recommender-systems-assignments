def computeMeanRating(filename):
    try:
        # create empty list for ratings
        ratings = []

        f = open(filename, 'r')
        # skip first line (i.e. headers)
        ratingsIter = iter(f)
        next(ratingsIter)
        for line in ratingsIter:
            ratings.append(float(line.split(',')[2]))

        rating_sum = 0
        for r in ratings:
            rating_sum += r

        # return mean
        return rating_sum / len(ratings)

    except FileNotFoundError as err:
        raise Exception('File "{0}" could not be found'.format(err.filename))
    except StopIteration:
        raise Exception('No read access to file')
    except ValueError:
        raise Exception('Cannot parse input - rating has invalid format')


def main():
    try:
        stats = computeMeanRating('resources/ratings.csv')
        print('Mean: {0}'.format(stats))
    except Exception as ex:
        print('An error occurred: {0}'.format(ex.args[0]))


main()
