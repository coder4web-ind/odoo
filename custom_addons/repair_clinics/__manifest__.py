{
    'name': 'Repair Clinics',
    'summary': 'Streamlined device repair tracking compliant with EU Directive 2024/1799 framework rules.',
    'version': '19.0.1.0.0',
    'category': 'Services',
    'author': 'Coder4Web',
    'website': 'mailto:coder4web@yahoo.com',
    'license': 'OPL-1',
    'price': '20.00',
    'currency': 'EUR',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/repair_brand.xml',
        'views/repair_category.xml',   
        'views/repair_device.xml', 
        'views/repair_job_view.xml',
        'views/menus/repair_clinics_menu.xml',
        'views/menus/repair_configuration_menu.xml',
    ],
    'demo': [
        'demo/repair_category_demo.xml',
        'demo/repair_brand_demo.xml',
        'demo/repair_device_demo.xml',
    ],
    'images': [
        'static/description/banner.png',        
        'static/description/repair_job.png'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}