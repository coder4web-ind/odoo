{
    'name': 'Repair Clinics',
    'version': '1.9',
    'category': 'Services/Repair',
    'sequence': 5,
    'summary': 'Core Booking & Device Tracking for Electronic Gadgets',
    'depends': ['base','repair_device','repair_status'],
    'author': 'Coder4web@yahoo.com',
    'data':[
        'data/default_records.xml',
        'security/ir.model.access.csv',        
        'views/res_company_view.xml',
        'views/repair_job_view.xml',
        'views/repair_job_type.xml',
        'views/menus/repair_clinics_menu.xml',
        'views/menus/repair_configuration_menu.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}