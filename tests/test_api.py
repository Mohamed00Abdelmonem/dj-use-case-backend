from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.people.models import Developer
from apps.gaps.models import GapClassification, Gap
from apps.integrations.models import Integration
from apps.portfolio.models import Domain, Category, UseCase

class APIEndpointsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.dev = Developer.objects.create(name="Alex Smith", role="Frontend Lead", email="alex@example.com")
        self.gc = GapClassification.objects.create(name="Technical", description="Tech debts")
        self.gap = Gap.objects.create(title="Legacy Auth", classification=self.gc, status="Open", priority="Critical")
        self.gap.owner_ids.add(self.dev)
        self.intg = Integration.objects.create(name="Payment Gateway", system="Stripe", status="Available")

        self.domain = Domain.objects.create(name="Finance", order=1)
        self.category = Category.objects.create(domain=self.domain, name="Billing", order=1)
        self.use_case = UseCase.objects.create(
            category=self.category,
            reference="UC-100",
            name="Invoice Generation",
            status="In Assessment"
        )
        self.use_case.developer_ids.add(self.dev)
        self.use_case.integration_ids.add(self.intg)
        self.use_case.gap_ids.add(self.gap)

    def test_settings_endpoint(self):
        res = self.client.get('/api/settings/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("useCaseStatuses", res.data)
        self.assertIn("gapStatuses", res.data)

    def test_portfolio_detail_endpoint(self):
        res = self.client.get('/api/portfolio/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("domains", res.data)
        self.assertEqual(len(res.data["domains"]), 1)

    def test_analytics_endpoint(self):
        res = self.client.get('/api/analytics/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("kpis", res.data)

    def test_developer_crud(self):
        res = self.client.post('/api/developers/', {
            "name": "Sam Taylor",
            "role": "Backend Dev",
            "email": "sam@example.com"
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        dev_id = res.data["id"]

        patch_res = self.client.patch(f'/api/developers/{dev_id}/', {"role": "Senior Dev"})
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)

        del_res = self.client.delete(f'/api/developers/{dev_id}/')
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

    def test_domain_delete_protected_when_has_categories(self):
        res = self.client.delete(f'/api/domains/{self.domain.id}/')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
