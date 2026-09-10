from django.test import TestCase
from apps.people.models import Developer
from apps.gaps.models import GapClassification, Gap
from apps.integrations.models import Integration
from apps.portfolio.models import Domain, Category, UseCase

class ModelTests(TestCase):
    def test_developer_creation(self):
        dev = Developer.objects.create(name="Jane Doe", role="Lead Dev", email="jane@example.com")
        self.assertTrue(dev.id.startswith("dev-"))
        self.assertEqual(str(dev), "Jane Doe")

    def test_gap_classification_and_gap(self):
        gc = GapClassification.objects.create(name="Security", description="Security gaps")
        self.assertTrue(gc.id.startswith("gclass-"))
        
        dev = Developer.objects.create(name="Security Lead")
        gap = Gap.objects.create(
            title="OAuth Missing",
            classification=gc,
            status="Open",
            priority="High"
        )
        gap.owner_ids.add(dev)
        self.assertTrue(gap.id.startswith("gap-"))
        self.assertEqual(gap.classification, gc)
        self.assertIn(dev, gap.owner_ids.all())

    def test_integration_creation(self):
        intg = Integration.objects.create(name="ERP Connector", system="SAP", status="Available")
        self.assertTrue(intg.id.startswith("int-"))
        self.assertEqual(str(intg), "ERP Connector")

    def test_domain_category_usecase_hierarchy(self):
        dom = Domain.objects.create(name="Sales", order=1)
        self.assertTrue(dom.id.startswith("dom-"))
        
        cat = Category.objects.create(domain=dom, name="CRM", order=1)
        self.assertTrue(cat.id.startswith("cat-"))
        self.assertEqual(cat.domain, dom)

        uc = UseCase.objects.create(
            category=cat,
            reference="UC-01",
            name="Lead Scoring",
            status="Ready"
        )
        self.assertTrue(uc.id.startswith("uc-"))
        self.assertEqual(uc.category, cat)
        self.assertEqual(uc.category.domain, dom)
