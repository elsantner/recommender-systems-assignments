def computeRatingStats(filename):
    try:
        # create empty list for ratings
        ratings = []

        f = open(filename, 'r')
        # skip first line (i.e. headers)
        ratingsIter = iter(f)
        next(ratingsIter)
        for line in ratingsIter:
            ratings.append(float(line.split(',')[2]))

        ratings.sort()

        rating_sum = 0
        # remember current mode
        cur = {'mode': -1.0, 'count': 0}
        temp = {'mode': -1.0, 'count': 0}
        for r in ratings:
            # works since ratings are sorted
            if r != temp['mode']:
                if temp['count'] > cur['count']:
                    cur['mode'] = temp['mode']
                    cur['count'] = temp['count']
                temp['count'] = 0
            temp['mode'] = r
            temp['count'] += 1

            rating_sum += r

        # return mean, median and mode
        return rating_sum / len(ratings), ratings[int(len(ratings) / 2)], cur['mode']

    except FileNotFoundError as err:
        raise Exception('File "{0}" could not be found'.format(err.filename))
    except StopIteration:
        raise Exception('No read access to file')
    except ValueError:
        raise Exception('Cannot parse input - rating has invalid format')


def main():
    try:
        stats = computeRatingStats('resources/ratings.csv')
        print('Mean: {0}, Median: {1}, Mode: {2}'.format(stats[0], stats[1], stats[2]))
    except Exception as ex:
        print('An error occurred: {0}'.format(ex.args[0]))


main()
