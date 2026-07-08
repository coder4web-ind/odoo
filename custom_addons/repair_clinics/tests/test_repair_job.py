# repair_clinics/tests/test_repair_job.py
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestRepairJob(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """ Runs once before all tests setup base data """
        super(TestRepairJob, cls).setUpClass()
        
        cls.customer = cls.env['res.partner'].create({
            'name': 'Test Walk-in Customer',
        })

        cls.mock_brand = cls.env['repair.device.brand'].create({
            'name': 'Apple',
            'code':'Apple'
        })

        cls.mock_category = cls.env['repair.device.category'].create({
            'name': 'Smartphones',
            'ranking':1
        })

        cls.mock_device = cls.env['repair.device'].create({
            'name': 'iPhone 15 Pro',
            'code':'iPhone 15 Pro',
            'description':'iPhone 15 Pro',
            'device_brand_id': cls.mock_brand.id,
            'device_category_id': cls.mock_category.id,
        })

        cls.sale_journal = cls.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', cls.env.company.id)
        ], limit=1)

        
        cls.mock_income_account = cls.env['account.account'].create({
            'name': 'Mock Repair Income Account',
            'code': '400000.MOCK',
            'account_type': 'income',
        })

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

        self.assertEqual(repair_job.state, 'draft')
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

        repair_job.state = 'done'
        action = repair_job.action_create_invoice()

        self.assertEqual(repair_job.state, 'delivered')
        self.assertTrue(repair_job.invoice_id)
        self.assertEqual(repair_job.invoice_id.invoice_line_ids[0].price_unit, 0.0)


    def test_03_prevent_double_invoicing(self):
        """ Ensure a job cannot be invoiced twice """
        repair_job = self.env['repair.job'].create({
            'name': 'RP-0003',
            'partner_id': self.customer.id,
            'device_brand_id': self.mock_brand.id,
            'device_category_id': self.mock_category.id,
            'device_id': self.mock_device.id,
            'summary': 'Battery replacement',
        })
        repair_job.state = 'done'
        
        # First creation succeeds
        repair_job.action_create_invoice()

        with self.assertRaises(UserError):
            repair_job.action_create_invoice()


    def test_04_delete_restrictions(self):
        """ Test that deletion is allowed in draft/received but blocked in done/delivered """
        # Case A: Deletion allowed in draft
        draft_job = self.env['repair.job'].create({
            'name': 'RP-DEL-01',
            'partner_id': self.customer.id,
            'device_brand_id': self.mock_brand.id,
            'device_category_id': self.mock_category.id,
            'device_id': self.mock_device.id,
            'state': 'draft',
            'summary': 'Battery replacement',
        })
        # This should execute without errors
        draft_job.unlink()

        # Case B: Deletion blocked in done
        secure_job = self.env['repair.job'].create({
            'name': 'RP-DEL-02',
            'partner_id': self.customer.id,
            'device_brand_id': self.mock_brand.id,
            'device_category_id': self.mock_category.id,
            'device_id': self.mock_device.id,
            'state': 'done',
            'summary': 'Battery replacement',
        })
        # This MUST raise a UserError and block the database drop
        with self.assertRaises(UserError):
            secure_job.unlink()