from django.core.paginator import Paginator

# количество постов на страницу
POSTS_PER_PAGE = 10


def paginator(request, list):
    paginator = Paginator(list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
