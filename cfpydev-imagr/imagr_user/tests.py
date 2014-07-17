from django.test import TestCase
from imagr_user.models import ImagrUser
from imagr_images.models import Photo, Album
from imagr_user.views import home
from django.test.client import Client, RequestFactory
from django.db import models
from django.core.files import File
from django.core.urlresolvers import reverse
from django.http import Http404
import os


class ImagrUser_Relations_Test(TestCase):

    def setUp(self):

        self.usr1 = ImagrUser(first_name='Eyuel', last_name='Abebe', username='Eyuel')
        self.usr2 = ImagrUser(first_name='Muazz', last_name='Mira', username='Muazz')
        self.usr3 = ImagrUser(first_name='Mike', last_name='Delany', username='Mike')

        self.usr1.save()
        self.usr2.save()
        self.usr3.save()

    def tearDown(self):

        self.usr1.delete()
        self.usr2.delete()
        self.usr3.delete()


    def test_user_creation(self):
        self.assertEqual(self.usr2.first_name, 'Muazz')
        self.assertEqual(self.usr2.last_name, 'Mira')

    def test_followers_following(self):

        self.usr1.follow(self.usr2)

        self.assertEqual(list(self.usr1.following()), [self.usr2])
        self.assertEqual(list(self.usr2.following()), [])

        self.assertEqual(self.usr1.following()[0], self.usr2)
        self.assertEqual(self.usr2.followers()[0], self.usr1)
        self.assertEqual(self.usr1.relationship_from.get(user_two=self.usr2).follower_status, 1)
        self.assertEqual(self.usr2.relationship_to.get(user_two=self.usr2).follower_status, 1)

        self.usr1.unfollow(self.usr2)

        self.assertEqual(list(self.usr1.following()), [])
        self.assertEqual(list(self.usr2.followers()), [])
        self.assertEqual(self.usr1.relationship_from.get(user_one=self.usr1).follower_status, 0)
        self.assertEqual(self.usr2.relationship_to.get(user_two=self.usr2).follower_status, 0)


    def test_friendship(self):

        self.usr1.request_friendship(self.usr2)

        usr1_friendship_status = self.usr1.relationship_from.get(user_two=self.usr2).friendship
        usr2_friendship_status = self.usr2.relationship_to.get(user_one=self.usr1).friendship

        self.assertEqual(usr1_friendship_status, 1)
        self.assertEqual(usr2_friendship_status, 1)

        self.usr2.accept_friendship_request(self.usr1)

        usr1_friendship_status = self.usr1.relationship_from.get(user_two=self.usr2).friendship
        usr2_friendship_status = self.usr1.relationship_from.get(user_one=self.usr1).friendship

        self.assertEqual(usr1_friendship_status, 3)
        self.assertEqual(usr2_friendship_status, 3)

        self.usr1.end_friendship(self.usr2)

        usr1_friendship_status = self.usr1.relationship_from.get(user_two=self.usr2).friendship
        usr2_friendship_status = self.usr1.relationship_from.get(user_one=self.usr1).friendship

        self.assertEqual(usr1_friendship_status, 0)
        self.assertEqual(usr2_friendship_status, 0)


    def test_list_friendship(self):

        self.usr1.request_friendship(self.usr2)
        self.usr1.request_friendship(self.usr3)
        self.usr2.request_friendship(self.usr3)

        self.usr2.accept_friendship_request(self.usr1)
        self.usr3.accept_friendship_request(self.usr1)
        self.usr3.accept_friendship_request(self.usr2)

        usr1_list_friends = self.usr1.list_friends()
        usr2_list_friends = self.usr2.list_friends()
        usr3_list_friends = self.usr3.list_friends()

        self.assertEqual(list(usr1_list_friends), [self.usr2, self.usr3])
        self.assertEqual(list(usr2_list_friends), [self.usr1, self.usr3])
        self.assertEqual(list(usr3_list_friends), [self.usr1, self.usr2])


class Home_test(TestCase):
    def setUp(self):
        # create users
        self.usr1 = ImagrUser.objects.create(first_name='Eyuel',
                                             last_name='Abebe',
                                             username='Eyuel')
        self.usr2 = ImagrUser.objects.create(first_name='Muazzez',
                                             last_name='Mira',
                                             username='Muazzez')
        self.factory = RequestFactory()
        # create photos
        base_dir = os.getcwd() + '/imagr_images/static/front_img/'
        with open(base_dir + '7fTNh.jpg', 'r') as f:
            photo_file = File(f)
            photo1 = Photo()
            photo1.image = photo_file
            photo1.title = 'horse'
            photo1.owner = self.usr1
            photo1.privacy_option = 2
            photo1.save()
        with open(base_dir + 'beer.jpg', 'r') as f:
            photo_file = File(f)
            photo2 = Photo()
            photo2.image = photo_file
            photo2.title = 'beer'
            photo2.owner = self.usr1
            photo2.privacy_option = 2
            photo2.save()

        # create album
        album1 = Album.objects.create(owner=self.usr1,
                                      title="album1",
                                      description="a1_descr",
                                      privacy_option=2)
        album1.photos = [photo1, photo2]

    def tearDown(self):
        self.usr1.delete()
        self.usr2.delete()

    def test_usr1_response(self):
        request = self.factory.get(reverse('home'))
        request.user = self.usr1
        response = home(request)
        self.assertEqual(response.status_code, 200)

    def test_usr2_response(self):
        request = self.factory.get(reverse('home'))
        request.user = self.usr2
        self.assertRaises(Http404, home, request)
