{
    "name": "Rikai Foresight",
    "summary": "Rikai Forsight",
    "version": "1.0",
    "category": "Rikai",
    "author": "Doan Hai Bang",
    "website": "http://www.rikai.technology",
    "application": True,
    "installable": True,
    'auto_install': False,
    'depends': ['base', 'mail'],
     "data": [
            'views/view_propose_payment.xml',
            'views/view_propose_budget.xml',
            'views/view_config_route.xml',
            'views/view_config_organization.xml',
            'data/security.xml',
            'views/view_script.xml',
            'views/view_config_budget_category.xml',
     ],

     'qweb': [
         'static/src/xml/organization.xml',
    #     'static/src/xml/project.xml',
    #     'static/src/xml/customer.xml',
    #     'static/src/xml/opportunity.xml',
     ]
    
}
