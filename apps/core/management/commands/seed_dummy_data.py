import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.portfolio.models import Domain, Category, UseCase, Pipeline
from apps.people.models import Developer
from apps.integrations.models import Integration, NAR
from apps.gaps.models import GapClassification, Gap


class Command(BaseCommand):
    help = 'Seeds database with realistic Use Case Hub dummy data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing portfolio data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options.get('reset', False)

        if reset:
            self.stdout.write(self.style.WARNING("Reset flag detected. Deleting existing portfolio data..."))
            Pipeline.objects.all().delete()
            NAR.objects.all().delete()
            UseCase.objects.all().delete()
            Category.objects.all().delete()
            Domain.objects.all().delete()
            Gap.objects.all().delete()
            GapClassification.objects.all().delete()
            Integration.objects.all().delete()
            Developer.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing portfolio data cleared."))

        # Locate seed JSON file
        current_dir = Path(__file__).resolve().parent
        candidate_paths = [
            current_dir.parent.parent / 'fixtures' / 'seed_data.json',
            Path(__file__).resolve().parents[3] / 'apps' / 'core' / 'fixtures' / 'seed_data.json',
            Path('/app/apps/core/fixtures/seed_data.json'),
        ]

        # Also check root or parent candidate paths
        for p in list(current_dir.parents):
            candidate_paths.append(p / 'use-case-hub-frontend' / 'public' / 'data' / 'use-case-hub.json')

        json_path = None
        for candidate in candidate_paths:
            if candidate.exists():
                json_path = candidate
                break

        if not json_path or not json_path.exists():
            self.stdout.write(self.style.ERROR("Seed JSON file not found!"))
            return

        self.stdout.write(f"Reading seed data from {json_path}...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        stats = {
            'developers': {'created': 0, 'updated': 0},
            'integrations': {'created': 0, 'updated': 0},
            'gap_classifications': {'created': 0, 'updated': 0},
            'gaps': {'created': 0, 'updated': 0},
            'domains': {'created': 0, 'updated': 0},
            'categories': {'created': 0, 'updated': 0},
            'use_cases': {'created': 0, 'updated': 0},
            'nars': {'created': 0, 'updated': 0},
            'pipelines': {'created': 0, 'updated': 0},
        }

        # 1. Developers
        dev_map = {}
        for dev_data in data.get('developers', []):
            dev_id = dev_data.get('id')
            if not dev_id:
                continue
            dev, created = Developer.objects.update_or_create(
                id=dev_id,
                defaults={
                    'name': dev_data.get('name', ''),
                    'role': dev_data.get('role', ''),
                    'email': dev_data.get('email', '')
                }
            )
            dev_map[dev.id] = dev
            stats['developers']['created' if created else 'updated'] += 1

        # 2. Integrations
        int_map = {}
        for int_data in data.get('integrations', []):
            int_id = int_data.get('id')
            if not int_id:
                continue
            integration, created = Integration.objects.update_or_create(
                id=int_id,
                defaults={
                    'name': int_data.get('name', ''),
                    'system': int_data.get('system', ''),
                    'source': int_data.get('source', ''),
                    'type': int_data.get('type', ''),
                    'direction': int_data.get('direction', ''),
                    'status': int_data.get('status', 'Not Started'),
                    'owner': int_data.get('owner', ''),
                    'owner_id': int_data.get('ownerId', ''),
                    'frequency': int_data.get('frequency', ''),
                    'data_objects': int_data.get('dataObjects', ''),
                    'description': int_data.get('description', '')
                }
            )
            int_map[integration.id] = integration
            stats['integrations']['created' if created else 'updated'] += 1

        # 3. Gap Classifications
        class_map = {}
        for class_data in data.get('gapClassifications', []):
            class_id = class_data.get('id')
            if not class_id:
                continue
            gc, created = GapClassification.objects.update_or_create(
                id=class_id,
                defaults={
                    'name': class_data.get('name', ''),
                    'description': class_data.get('description', '')
                }
            )
            class_map[gc.id] = gc
            stats['gap_classifications']['created' if created else 'updated'] += 1

        # 4. Gaps
        gap_map = {}
        for gap_data in data.get('gaps', []):
            gap_id = gap_data.get('id')
            if not gap_id:
                continue
            c_id = gap_data.get('classificationId')
            gc = class_map.get(c_id) if c_id else None
            gap, created = Gap.objects.update_or_create(
                id=gap_id,
                defaults={
                    'title': gap_data.get('title', ''),
                    'description': gap_data.get('description', ''),
                    'classification': gc,
                    'status': gap_data.get('status', 'Open'),
                    'priority': gap_data.get('priority', 'Medium'),
                    'due_date': gap_data.get('dueDate', ''),
                    'dependency': gap_data.get('dependency', ''),
                    'resolution': gap_data.get('resolution', '')
                }
            )
            owner_ids = [dev_map[o_id] for o_id in gap_data.get('ownerIds', []) if o_id in dev_map]
            gap.owner_ids.set(owner_ids)
            gap_map[gap.id] = gap
            stats['gaps']['created' if created else 'updated'] += 1

        # 5. Domains, Categories & Use Cases
        uc_map = {}
        for dom_data in data.get('domains', []):
            dom_id = dom_data.get('id')
            if not dom_id:
                continue
            domain, created = Domain.objects.update_or_create(
                id=dom_id,
                defaults={
                    'name': dom_data.get('name', ''),
                    'description': dom_data.get('description', ''),
                    'order': dom_data.get('order', 1)
                }
            )
            stats['domains']['created' if created else 'updated'] += 1

            for cat_data in dom_data.get('categories', []):
                cat_id = cat_data.get('id')
                if not cat_id:
                    continue
                category, created = Category.objects.update_or_create(
                    id=cat_id,
                    defaults={
                        'domain': domain,
                        'name': cat_data.get('name', ''),
                        'description': cat_data.get('description', ''),
                        'order': cat_data.get('order', 1)
                    }
                )
                stats['categories']['created' if created else 'updated'] += 1

                for uc_data in cat_data.get('useCases', []):
                    uc_id = uc_data.get('id')
                    if not uc_id:
                        continue
                    uc, created = UseCase.objects.update_or_create(
                        id=uc_id,
                        defaults={
                            'category': category,
                            'reference': uc_data.get('reference', ''),
                            'name': uc_data.get('name', ''),
                            'description': uc_data.get('description', ''),
                            'business_value': uc_data.get('businessValue', ''),
                            'outputs': uc_data.get('outputs', ''),
                            'status': uc_data.get('status', 'Not Assessed'),
                            'notes': uc_data.get('notes', '')
                        }
                    )
                    uc_map[uc.id] = uc
                    stats['use_cases']['created' if created else 'updated'] += 1

                    dev_objs = [dev_map[d_id] for d_id in uc_data.get('developerIds', []) if d_id in dev_map]
                    int_objs = [int_map[i_id] for i_id in uc_data.get('integrationIds', []) if i_id in int_map]
                    gap_objs = [gap_map[g_id] for g_id in uc_data.get('gapIds', []) if g_id in gap_map]

                    uc.developer_ids.set(dev_objs)
                    uc.integration_ids.set(int_objs)
                    uc.gap_ids.set(gap_objs)

        # 6. NARs
        nars_seed = data.get('nars')
        if not nars_seed:
            available_int_ids = list(int_map.keys())
            available_dev_ids = list(dev_map.keys())
            nars_seed = [
                {
                    "id": "nar-2026-001",
                    "number": "NAR-2026-001",
                    "status": "Approved",
                    "requestDate": "2026-01-15",
                    "endDate": "2026-12-31",
                    "warningDays": 30,
                    "mailSubject": "Firewall & DB Access for Pega & CMS Integrations",
                    "requester": "Walid Gamal / Core Operations",
                    "approvalReference": "CHG-998822",
                    "integrationIds": available_int_ids[:2],
                    "ownerIds": available_dev_ids[:1],
                    "accessScope": "Read/write access to Pega reactive tickets and CMS Change Management DB.",
                    "notes": "Annual renewal approved by IT Security."
                },
                {
                    "id": "nar-2026-002",
                    "number": "NAR-2026-002",
                    "status": "Submitted",
                    "requestDate": "2026-08-01",
                    "endDate": "2026-10-15",
                    "warningDays": 30,
                    "mailSubject": "SNMP Inbound Trap Access for Watson Alarms",
                    "requester": "Hend Mohamed / Monitoring Team",
                    "approvalReference": "INC-445511",
                    "integrationIds": available_int_ids[2:4],
                    "ownerIds": available_dev_ids[1:2],
                    "accessScope": "SNMP trap receiver port 162 access for Watson alarm integration.",
                    "notes": "Under review by Network Security."
                },
                {
                    "id": "nar-2026-003",
                    "number": "NAR-2026-003",
                    "status": "Draft",
                    "requestDate": "2026-09-01",
                    "endDate": "2027-03-31",
                    "warningDays": 30,
                    "mailSubject": "Granite Data Single Store API Integration Access",
                    "requester": "Oraby Mahmoud / Data Team",
                    "approvalReference": "CHG-100234",
                    "integrationIds": available_int_ids[4:6],
                    "ownerIds": available_dev_ids[2:3],
                    "accessScope": "API endpoint access for Single Store topology & inventory data query.",
                    "notes": "Drafting initial security questionnaire."
                }
            ]

        for nar_data in nars_seed:
            nar_id = nar_data.get('id')
            if not nar_id:
                continue
            nar, created = NAR.objects.update_or_create(
                id=nar_id,
                defaults={
                    'number': nar_data.get('number', ''),
                    'status': nar_data.get('status', 'Draft'),
                    'request_date': nar_data.get('requestDate', ''),
                    'end_date': nar_data.get('endDate', ''),
                    'warning_days': nar_data.get('warningDays', 30),
                    'mail_subject': nar_data.get('mailSubject', ''),
                    'requester': nar_data.get('requester', ''),
                    'approval_reference': nar_data.get('approvalReference', ''),
                    'access_scope': nar_data.get('accessScope', ''),
                    'notes': nar_data.get('notes', '')
                }
            )
            int_objs = [int_map[i_id] for i_id in nar_data.get('integrationIds', []) if i_id in int_map]
            owner_objs = [dev_map[o_id] for o_id in nar_data.get('ownerIds', []) if o_id in dev_map]
            nar.integration_ids.set(int_objs)
            nar.owner_ids.set(owner_objs)
            stats['nars']['created' if created else 'updated'] += 1

        # 7. Pipelines
        pipes_seed = data.get('pipelines')
        if not pipes_seed:
            available_int_ids = list(int_map.keys())
            available_uc_ids = list(uc_map.keys())
            available_dev_ids = list(dev_map.keys())
            pipes_seed = [
                {
                    "id": "pipe-001",
                    "name": "MDT Customer Impact Pipeline",
                    "uuid": "mdt_customer_impact_v2",
                    "type": "Batch",
                    "status": "Active",
                    "server": "mage-prod-01",
                    "serverUrl": "https://mage.internal/pipelines/mdt_customer_impact_v2",
                    "environment": "Production",
                    "schedule": "*/15 * * * *",
                    "timezone": "UTC",
                    "repositoryUrl": "https://github.com/selecteg/mage-mdt-impact",
                    "pipelinePath": "pipelines/mdt_customer_impact_v2",
                    "integrationIds": available_int_ids[:2],
                    "useCaseIds": available_uc_ids[:2],
                    "ownerIds": available_dev_ids[:1],
                    "blocks": [
                        { "order": 1, "type": "data_loader", "name": "Load MDT Tickets", "uuid": "load_mdt_tickets" },
                        { "order": 2, "type": "transformer", "name": "Calculate Impacted Customers", "uuid": "calc_impact" },
                        { "order": 3, "type": "data_exporter", "name": "Export to SingleStore", "uuid": "export_singlestore" }
                    ],
                    "description": "Processes MDT customer impact telemetry and feeds affected service count to SingleStore.",
                    "notes": "Runs every 15 minutes."
                },
                {
                    "id": "pipe-002",
                    "name": "Alarm Correlation & Incident Ingestion",
                    "uuid": "alarm_correlation_stream",
                    "type": "Streaming",
                    "status": "In Development",
                    "server": "mage-dev-02",
                    "serverUrl": "https://mage-dev.internal/pipelines/alarm_correlation_stream",
                    "environment": "Development",
                    "schedule": "Real-time",
                    "timezone": "UTC",
                    "repositoryUrl": "https://github.com/selecteg/mage-alarm-correlation",
                    "pipelinePath": "pipelines/alarm_correlation_stream",
                    "integrationIds": available_int_ids[2:4],
                    "useCaseIds": available_uc_ids[2:4],
                    "ownerIds": available_dev_ids[1:2],
                    "blocks": [
                        { "order": 1, "type": "data_loader", "name": "Stream Watson Alarms", "uuid": "stream_watson" },
                        { "order": 2, "type": "transformer", "name": "Correlate Network Alarms", "uuid": "correlate_alarms" },
                        { "order": 3, "type": "data_exporter", "name": "Create RTTS Proactive Ticket", "uuid": "export_rtts" }
                    ],
                    "description": "Real-time correlation of incoming Watson network alarms into parent/child incident clusters.",
                    "notes": "Currently testing streaming memory consumption."
                }
            ]

        for pipe_data in pipes_seed:
            pipe_id = pipe_data.get('id')
            if not pipe_id:
                continue
            pipeline, created = Pipeline.objects.update_or_create(
                id=pipe_id,
                defaults={
                    'name': pipe_data.get('name', ''),
                    'uuid': pipe_data.get('uuid', ''),
                    'type': pipe_data.get('type', 'Batch'),
                    'status': pipe_data.get('status', 'Planned'),
                    'server': pipe_data.get('server', ''),
                    'server_url': pipe_data.get('serverUrl', ''),
                    'environment': pipe_data.get('environment', 'Development'),
                    'schedule': pipe_data.get('schedule', ''),
                    'timezone': pipe_data.get('timezone', 'UTC'),
                    'repository_url': pipe_data.get('repositoryUrl', ''),
                    'pipeline_path': pipe_data.get('pipelinePath', ''),
                    'blocks': pipe_data.get('blocks', []),
                    'description': pipe_data.get('description', ''),
                    'notes': pipe_data.get('notes', '')
                }
            )
            int_objs = [int_map[i_id] for i_id in pipe_data.get('integrationIds', []) if i_id in int_map]
            uc_objs = [uc_map[u_id] for u_id in pipe_data.get('useCaseIds', []) if u_id in uc_map]
            owner_objs = [dev_map[o_id] for o_id in pipe_data.get('ownerIds', []) if o_id in dev_map]
            pipeline.integration_ids.set(int_objs)
            pipeline.use_case_ids.set(uc_objs)
            pipeline.owner_ids.set(owner_objs)
            stats['pipelines']['created' if created else 'updated'] += 1

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully! Summary of operations:"))
        for entity, counts in stats.items():
            self.stdout.write(f"  - {entity.replace('_', ' ').capitalize()}: {counts['created']} created, {counts['updated']} updated")
