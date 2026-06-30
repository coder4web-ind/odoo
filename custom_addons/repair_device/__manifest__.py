{
    'name': 'Repair Devices Master Data',
    'version': '19.0.1.0',
    'category': 'Services/Repair',
    'summary': 'Master Catalog for Electronics Manufacturers and Models',
    'depends': ['base'],
    'data':[
        'security/ir.model.access.csv',
        'security/repair_security.xml',
        'views/repair_device_manufacturer.xml',
        'views/reapir_device_model.xml'
    ],
    'author': 'Coder4web@yahoo.com',
    'installable': True,
    'application': False,  # This is a backend library/dependency app
    'license': 'LGPL-3',
}