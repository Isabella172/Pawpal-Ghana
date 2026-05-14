from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        self.refresh_url = reverse('token-refresh')
        self.user_data = {
            'email': 'owner@example.com',
            'phone_number': '+233240000000',
            'role': 'owner',
            'password': 'StrongPass123',
            'password_confirm': 'StrongPass123',
        }

    def register_user(self):
        return self.client.post(self.register_url, self.user_data, format='json')

    def test_register_returns_jwt_tokens(self):
        response = self.register_user()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_register_rejects_invalid_ghana_phone_number(self):
        payload = {
            **self.user_data,
            'email': 'bad-phone@example.com',
            'phone_number': '0240000000',
        }

        response = self.client.post(self.register_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data)

    def test_register_rejects_password_mismatch(self):
        payload = {**self.user_data, 'password_confirm': 'WrongPass123'}

        response = self.client.post(self.register_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_email_returns_jwt_tokens(self):
        self.register_user()

        response = self.client.post(
            self.login_url,
            {'email': self.user_data['email'], 'password': self.user_data['password']},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_profile_get_and_patch_with_jwt_token(self):
        register_response = self.register_user()
        access_token = register_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        get_response = self.client.get(self.profile_url)
        patch_response = self.client.patch(
            self.profile_url,
            {'first_name': 'Ama', 'last_name': 'Owusu'},
            format='json',
        )

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['email'], self.user_data['email'])
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['first_name'], 'Ama')
        self.assertEqual(patch_response.data['last_name'], 'Owusu')

    def test_refresh_endpoint_returns_new_access_token(self):
        register_response = self.register_user()
        refresh_token = register_response.data['tokens']['refresh']

        response = self.client.post(
            self.refresh_url,
            {'refresh': refresh_token},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
