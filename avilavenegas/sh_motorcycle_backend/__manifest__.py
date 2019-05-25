# -*- coding: utf-8 -*-

{
    "name": "Motorcycle Backend",
    "author": " ",
    "website": "",
    "support": "",
    "category": "",
    "summary": "",
    "description": """
                    """,
    "version": "12.0.0",
    "depends": [
                    "base",
                    "product",
                    "stock",
                    "sale",
                ],
    "application": True,
    "data": [
            "data/motorcycle_data.xml",
            "security/motorcycle_security.xml",
            "security/ir.model.access.csv",
            "views/motorcycle_view.xml",
            "views/type_view.xml",
            "views/make_view.xml",
            "views/mmodel_view.xml",
            "views/year_view.xml",
            "views/product_view.xml",
            ],
    "auto_install": False,
    "installable": True,
}
