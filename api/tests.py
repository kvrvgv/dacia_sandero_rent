

from django.test import TestCase, Client as DjangoClient
from django.urls import reverse

from .models import *


class PlansViewTests(TestCase):
    def setUp(self):
        self.django_client = DjangoClient()
        self.client = Client(username="gribtest", password="GribTest1!")
        self.client.save()
        self.plans = Plan(name="TestPlan", price=1000, description="t", time_min=100)
        self.plans.save()

    def test_ok(self):
        self.django_client.force_login(self.client)
        response = self.django_client.get(reverse("available_plans"))
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("success", json_response)
        self.assertTrue(json_response["success"])
        self.assertIn("data", json_response)
        data = json_response["data"]
        self.assertEqual(len(data), 1)
        data = data.pop()
        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("price", data)
        self.assertIn("description", data)


class PlansEmptyViewTests(TestCase):
    def setUp(self):
        self.django_client = DjangoClient()
        self.client = Client(username="gribtest", password="GribTest1!")
        self.client.save()

    def test_empty_plans_db(self):
        self.django_client.force_login(self.client)
        response = self.django_client.get(reverse("available_plans"))
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("success", json_response)
        self.assertTrue(json_response["success"])
        self.assertIn("data", json_response)
        data = json_response["data"]
        self.assertEqual(len(data), 0)


class AvailableTransportsNoOnParkingViewTests(TestCase):
    def setUp(self):
        self.django_client = DjangoClient()
        self.client = Client(username="gribtest", password="GribTest1!")
        self.client.save()
        self.parking = ParkingStation(address="asd", short_name="sodos", max_cars=15)
        self.parking.save()

    def test_available_cars_ok_but_no_cars_on_this_parking(self):
        self.django_client.force_login(self.client)
        response = self.django_client.get(reverse("available_transport"))
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("success", json_response)
        self.assertTrue(json_response["success"])
        self.assertIn("data", json_response)
        data = json_response["data"]
        self.assertEqual(len(data), 1)
        data = data.pop()
        self.assertIn("id", data)
        self.assertIn("address", data)
        self.assertIn("shortName", data)
        self.assertIn("maxCars", data)
        self.assertIn("occupancy", data)
        self.assertIn("availableModels", data)
        self.assertEqual(len(data['availableModels']), 0)


class AvailableTransportsEmptyDbViewTests(TestCase):
    def setUp(self):
        self.django_client = DjangoClient()
        self.client = Client(username="gribtest", password="GribTest1!")
        self.client.save()

    def test_available_cars_empty(self):
        self.django_client.force_login(self.client)
        response = self.django_client.get(reverse("available_transport"))
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("success", json_response)
        self.assertTrue(json_response["success"])
        self.assertIn("data", json_response)
        data = json_response["data"]
        self.assertEqual(len(data), 0)


class AvailableTransportGoodViewTests(TestCase):
    def setUp(self):
        self.django_client = DjangoClient()
        self.client = Client(username="gribtest", password="GribTest1!")
        self.client.save()
        self.parking = ParkingStation(address="asd", short_name="sodos", max_cars=15)
        self.parking.save()
        self.transport_type = TransportType(name="aboba")
        self.transport_type.save()
        self.transport_class = TransportClass(name="sosoos", minimal_rating=10)
        self.transport_class.save()
        self.model = TransportModel(
            type=self.transport_type,
            classification=self.transport_class,
            name="kia rio sport gt x 100 gigabyte ultra hd 4k hot moms boobs",
            description="hello, road =)",
            image="/home/images/ava_bomba.jpeg_mafia"
        )
        self.model.save()
        self.transport = Transport(
            model=self.model,
            parking=self.parking,
            fuel=100,
            registry_number="606060"
        )
        self.transport.save()

    def test_available_cars_ok(self):
        self.django_client.force_login(self.client)
        response = self.django_client.get(reverse("available_transport"))
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("success", json_response)
        self.assertTrue(json_response["success"])
        self.assertIn("data", json_response)
        data = json_response["data"]
        self.assertEqual(len(data), 1)
        data = data.pop()
        self.assertIn("id", data)
        self.assertIn("address", data)
        self.assertIn("shortName", data)
        self.assertIn("maxCars", data)
        self.assertIn("occupancy", data)
        self.assertIn("availableModels", data)
        self.assertEqual(len(data['availableModels']), 1)
        available_model = data['availableModels'].pop()
        self.assertEqual(available_model["count"], 1)
        self.assertIn("id", available_model)
        self.assertIn("type", available_model)
        self.assertIn("classification", available_model)
        self.assertIn("name", available_model)
        self.assertIn("description", available_model)
        self.assertIn("imageUrl", available_model)
