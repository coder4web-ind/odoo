{
    'name': 'Repair Clinics',
    'version': '19.0.1.0.0',
    'category': 'Services/Repair',
    'sequence': 5,
    'summary': 'Core Booking & Device Tracking for Electronic Gadgets',
    'depends': ['base','account','mail','repair_device'],
    'author': 'Coder4web@yahoo.com',
    'data':[
        
        'security/ir.model.access.csv',        
        'views/repair_job_view.xml',        
        'views/menus/repair_clinics_menu.xml',
        'views/menus/repair_configuration_menu.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}