from django.http import HttpResponse
from django.template import loader
from .modules import nearest_neighbor as nn
from .modules import data_utils as dat


# base file for the two views: index and result


def index(request):
    context = {}
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))


def result(request):
    # read all ratings
    movie_ratings = dat.read_ratings()

    # create the user-item-matrix with the given ratings
    userItemMatrix = nn.create_user_item_matrix(movie_ratings)

    # get the top-recommendations for a specific user (entered in form)
    recommendations = nn.get_recommendations(movie_ratings, userItemMatrix, int(request.POST['userId']), 20)

    # to_html() creates a table in html code from a dataframe
    movie_metadata = dat.get_movies_metadata(recommendations)

    context = {'userId': request.POST['userId'],
               'metadata': movie_metadata}

    # load the template
    template = loader.get_template('recommendations.html')

    # render the template with the context
    return HttpResponse(template.render(context, request))
