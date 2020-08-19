from django.urls import reverse
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest


class TestLocation(ParentTest):
    def test_locations(self):
        self.assertEqual(Region.objects.count(), 2)
        self.assertEqual(District.objects.count(), 2)
        self.assertEqual(County.objects.count(), 2)
        self.assertEqual(SubCounty.objects.count(), 2)
        self.assertEqual(Parish.objects.count(), 2)
        self.assertEqual(Village.objects.count(), 2)

    def test_location_endpoints(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("districts")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 2)

        url = reverse("counties")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 2)

        url = reverse("subcounties")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 2)

        url = reverse("parishes")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 2)

        url = reverse("villages")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 2)
