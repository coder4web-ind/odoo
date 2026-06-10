{
    'name': 'Repair Clinics',
    'version': '1.9',
    'category': 'Services/Repair',
    'sequence': 5,
    'summary': 'Core Booking & Device Tracking for Electronic Gadgets',
    'depends': ['base','repair_device','repair_status'],
    'author': 'Coder4web@yahoo.com',
    'data':[
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}