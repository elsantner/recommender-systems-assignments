import csv


def analyzeGenres(filename):
    try:
        with open(filename, encoding='utf-8') as csv_file:
            file = csv.DictReader(csv_file)

            genre_count = dict()
            for row in file:
                for genre in row['genres'].split('|'):
                    if genre in genre_count:
                        genre_count[genre] += 1
                    else:
                        genre_count[genre] = 1

            sorted_dict = {k: v for k, v in sorted(genre_count.items(), key=lambda item: item[1], reverse=True)}
            print('MOVIE GENRES (Descending popularity)')
            for key in sorted_dict.keys():
                print('{0}: {1}'.format(key, genre_count[key]))

    except FileNotFoundError as err:
        raise Exception('File "{0}" could not be found'.format(err.filename))
    except StopIteration:
        raise Exception('No read access to file')


def main():
    try:
        analyzeGenres('resources/movies.csv')
    except Exception as ex:
        print('An error occurred: {0}'.format(ex.args[0]))


main()
