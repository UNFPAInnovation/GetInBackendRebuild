from app.models import Disability


def setup_disabilities():
    try:
        # count check prevents ERROR: You can't execute queries until the end of the 'atomic' block.
        if Disability.objects.count() == 0:
            Disability.objects.create(name='seeing', description='I have challenges with seeing different objects')
            Disability.objects.create(name='walking', description='I have challenges walking/climbing some places')
            Disability.objects.create(name='hearing', description='I have challenges with hearing some of the words people say')
            Disability.objects.create(name='bathing', description='I have challenges with bathing myself/getting dressed')
            Disability.objects.create(name='mental',
                                      description='I have some mental impairment issues/mad person/forget so easily')
            Disability.objects.create(name='albino', description='I am an Albino')
            Disability.objects.create(name='other', description='Other form of disability')
    except Exception as e:
        print(e)
    return True
