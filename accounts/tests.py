from eth_account import Account
from eth_account.messages import encode_defunct
from rest_framework.test import APITestCase

from accounts.models import WalletNonce


class WalletAuthTests(APITestCase):
    def test_nonce_issuance(self):
        acct = Account.create()
        response = self.client.post('/api/auth/nonce/', {'wallet': acct.address}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('nonce', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['wallet'], acct.address)
        self.assertTrue(WalletNonce.objects.filter(wallet=acct.address, nonce=response.data['nonce']).exists())

    def test_wallet_login_success(self):
        acct = Account.create()
        nonce_response = self.client.post('/api/auth/nonce/', {'wallet': acct.address}, format='json')
        nonce = nonce_response.data['nonce']
        message = nonce_response.data['message']

        signed = Account.sign_message(encode_defunct(text=message), acct.key)
        login_response = self.client.post(
            '/api/auth/wallet-login/',
            {'wallet': acct.address, 'nonce': nonce, 'signature': signed.signature.hex()},
            format='json',
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)
        self.assertEqual(login_response.data['user']['wallet'], acct.address)
        self.assertFalse(login_response.data['user']['is_employer_registered'])


from django.contrib.auth.models import User

from accounts.models import UserProfile


class EmployerRequiredTests(APITestCase):
    def test_payroll_endpoint_requires_employer_registration(self):
        user = User.objects.create_user(username='wallet_0xtest')
        UserProfile.objects.create(user=user, wallet_address='0x' + '1' * 40)
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/payroll/schedules/create/', {'name': 'Weekly', 'schedule_type': 'weekly', 'weekday': 1}, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], 'Employer profile not set. Register name and email first.')
