# repair_clinics/tests/test_repair_job.py
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestRepairJob(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """ Runs once before all tests setup base data """
        super(TestRepairJob, cls).setUpClass()
        
        # 1. Create a mock customer for testing
        cls.customer = cls.env['res.partner'].create({
            'name': 'Test Walk-in Customer',
        })

        # 2. Create foundational required infrastructure records
        cls.mock_brand = cls.env['repair.device.brand'].create({
            'name': 'Apple',
            'code':'Apple'
        })

        cls.mock_category = cls.env['repair.device.category'].create({
            'name': 'Smartphones',
            'ranking':1
        })

        # Create the mock device linking to the brand and category above
        cls.mock_device = cls.env['repair.device'].create({
            'name': 'iPhone 15 Pro',
            'code':'iPhone 15 Pro',
            'description':'iPhone 15 Pro',
            'device_brand_id': cls.mock_brand.id,
            'device_category_id': cls.mock_category.id,
        })

        # 3. Get the clean Sales Journal created by Odoo
        cls.sale_journal = cls.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', cls.env.company.id)
        ], limit=1)

        # 4. Create a clean mock income account using pure Odoo 19 syntax
        cls.mock_income_account = cls.env['account.account'].create({
            'name': 'Mock Repair Income Account',
            'code': '400000.MOCK',
            'account_type': 'income',
        })

        # 5. Set the default account on the sales journal as a fallback
        cls.sale_journal.default_account_id = cls.mock_income_account.id

    def test_01_initial_state_and_invoice_button(self):
        """ Test that a new repair job starts in draft and invoice creation fails """
        repair_job = self.env['repair.job'].create({
            'name': 'RP-0001',
            'partner_id': self.customer.id,
            'device_brand_id': self.mock_brand.id,
            'device_category_id': self.mock_category.id,
            'device_id': self.mock_device.id,
            'summary': 'Broken screen replacement',
        })

        # Verify initial state is draft
        self.assertEqual(repair_job.state, 'draft')

        # Verify that clicking 'Create Invoice' in draft raises a UserError
        with self.assertRaises(UserError):
            repair_job.action_create_invoice()

    def test_02_successful_invoice_generation(self):
        """ Test moving to 'done' and generating a draft invoice """
        repair_job = self.env['repair.job'].create({
            'name': 'RP-0002',
            'partner_id': self.customer.id,
            'device_brand_id': self.mock_brand.id,
            'device_category_id': self.mock_category.id,
            'device_id': self.mock_device.id,
            'summary': 'Battery replacement',
        })

        # Simulate moving through workflow to 'done'
        repair_job.state = 'done'

        # Trigger invoice action
        action = repair_job.action_create_invoice()

        # Assert state changed to delivered
        self.assertEqual(repair_job.state, 'delivered')
        # Assert invoice record was created and linked
        self.assertTrue(repair_job.invoice_id)
        # Assert the invoice starts at a price of 0.0 as intended
        self.assertEqual(repair_job.invoice_id.invoice_line_ids[0].price_unit, 0.0)