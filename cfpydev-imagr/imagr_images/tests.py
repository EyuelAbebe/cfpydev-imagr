from django.test import TestCase
from imagr_images.models import Photo, Album, ImagrUser, Relationships
from imagr_images.views import albumView, photoView, streamView
import datetime
from django.test.client import RequestFactory
from django.core.files import File
from django.core.urlresolvers import reverse
import os


class PhotoTests(TestCase):

    def test_photo_creation(self):
        photo1 = Photo(title='test_title',
                       description='test_description',
                       date_uploaded=datetime.datetime.now(),
                       privacy_option=1)

        self.assertEqual(photo1.title, 'test_title')
        self.assertEqual(photo1.description, 'test_description')
        self.assertEqual(photo1.privacy_option, 1)

class AlbumTests(TestCase):
    def test_album_creation(self):
        album1 = Album(title="album1",
                       description="test album 1",
                       privacy_option=1,
                      )
        self.assertEqual(album1.title, "album1")
        self.assertEqual(album1.description, "test album 1")
        self.assertEqual(album1.privacy_option, 1)


class test_albumView(TestCase):

    def setUp(self):
        self.usr1 = ImagrUser(first_name='Eyuel', last_name='Abebe', username='Eyuel')
        self.usr1.save()

        test_image_path = os.path.dirname(__file__) + '/test_files/ocean.jpg'
        image = File(open(test_image_path, 'rb'))
        self.photo = Photo.objects.create(owner=self.usr1,
                                          image=image,
                                          title='ocean',
                                          description='Test pic',
                                          privacy_option=2)

        self.album = Album.objects.create(owner=self.usr1,
                                          title="ocean",
                                          description='Test album',
                                          privacy_option=2)
        self.album.photos = [self.photo]
        self.factory = RequestFactory()


    def test_albumView(self):
        request = self.factory.get(reverse('home'))
        request.user = self.usr1
        response = albumView(request, 1)
        self.assertEqual(response.status_code, 200)
        content = response.content
        title_test = self.album.photos in content
        self.assertEqual(title_test, True)


class test_photoView(TestCase):

    def setUp(self):
        self.usr1 = ImagrUser(first_name='Eyuel', last_name='Abebe', username='Eyuel')
        self.usr1.save()

        test_image_path = os.path.dirname(__file__) + '/test_files/ocean.jpg'
        image = File(open(test_image_path, 'rb'))
        self.photo = Photo.objects.create(owner=self.usr1,
                                          image=image,
                                          title='ocean',
                                          description='Test pic',
                                          privacy_option=2)

        self.album = Album.objects.create(owner=self.usr1,
                                          title="ocean",
                                          description='Test album',
                                          privacy_option=2)
        self.album.photos = [self.photo]

        self.factory = RequestFactory()

    def tearDown(self):
        self.usr1.delete()
        self.photo.delete()
        self.album.delete()

    def test_albumView(self):
        request = self.factory.get(reverse('home'))
        request.user = self.usr1
        response = photoView(request, 1)
        self.assertEqual(response.status_code, 200)

        content = response.content
        # import pdb;pdb.set_trace()
        title_test = self.photo.title in content
        description_test = self.photo.description in content

        self.assertEqual(title_test, True)
        self.assertEqual(description_test, True)


class StreamViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.usr1 = ImagrUser(first_name='Eyuel', last_name='Abebe', username='Eyuel')
        self.usr2 = ImagrUser(first_name='Muazz', last_name='Mira', username='Muazz')
        self.usr3 = ImagrUser(first_name='Mike', last_name='Delany', username='Mike')
        self.usr4 = ImagrUser(first_name='Sean', last_name='SeanLast', username='Sean')
        self.usr5 = ImagrUser(first_name='John', last_name='Shiver', username='John')

        self.usr1.save()
        self.usr2.save()
        self.usr3.save()
        self.usr4.save()
        self.usr5.save()

        user_list = [ self.usr1, self.usr2, self.usr3, self.usr4]

        photo_list = ["{}_{}_{}".format("photo", item.username, i) for item in user_list for i in range(5)]
        base = datetime.datetime.today()
        date_list = [base - datetime.timedelta(days=x) for x in range(0, 20)]
        date_index = 0
        user_index = 0
        with open('/Users/muazzezmira/projects/django_imagr/cfpydev-imagr/cfpydev-imagr/imagr_images/static/front_img/7fTNh.jpg', 'rb') as f:
            for item in photo_list:
                photo_file = File(f)
                photo = Photo()
                photo.image = photo_file
                photo.title = item
                photo.owner = user_list[user_index]
                photo.privacy_option = 2
                photo.date_uploaded=date_list[date_index]
                photo.save()
                date_index +=1
                if not date_index % 5:
                    user_index += 1
                photo.save()

        self.usr1.request_friendship(self.usr2)
        self.usr2.accept_friendship_request(self.usr1)

        self.usr2.request_friendship(self.usr4)
        self.usr4.accept_friendship_request(self.usr2)

        self.usr1.follow(self.usr3)
        self.usr4.follow(self.usr1)
        self.usr1.follow(self.usr5)
        self.usr5.follow(self.usr1)


    def tearDown(self):

        self.usr1.delete()
        self.usr2.delete()
        self.usr3.delete()
        self.usr4.delete()
        self.usr5.delete()


    def test_stream(self):
        db_photo_list = {}
        db_photo_list[self.usr1] = Photo.objects.filter(owner__exact=self.usr1.id)
        db_photo_list[self.usr2] = Photo.objects.filter(owner__exact=self.usr2.id)
        db_photo_list[self.usr3] = Photo.objects.filter(owner__exact=self.usr3.id)
        db_photo_list[self.usr4] = Photo.objects.filter(owner__exact=self.usr4.id)
        db_photo_list[self.usr5] = Photo.objects.filter(owner__exact=self.usr5.id)

        assert len(db_photo_list[self.usr1]) == 5
        assert len(db_photo_list[self.usr2]) == 5
        assert len(db_photo_list[self.usr3]) == 5
        assert len(db_photo_list[self.usr4]) == 5
        assert len(db_photo_list[self.usr5]) == 0

        friend_following_list = [self.usr1, self.usr2, self.usr3]
        non_ff_list = [self.usr4, self.usr5]

        request = self.factory.get('/stream/')
        request.user = self.usr1
        response = streamView(request)
        self.assertEqual(response.status_code, 200)

        response = str(response)

        for user in friend_following_list:
            for photo in db_photo_list[user]:
                assert photo.title  in response

        for user in non_ff_list:
            for photo in db_photo_list[user]:
                assert str(photo) not in response

