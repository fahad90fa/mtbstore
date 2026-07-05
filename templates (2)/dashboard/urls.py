from django.urls import path
from . import views, inventory, merchants, employees, clients, profile, dashboard
urlpatterns = [
    path("api/alerts/", views.alerts_api, name="alerts_api"),
    path("api/alerts/read/<int:alert_id>/", views.mark_alert_read, name="alert_read"),


    path("api/templates/", views.templates_api, name="templates_api"),
    path("api/invoice/popup/drafts/", views.popup_fetch_drafts, name="popup_fetch_drafts"),





    # ───────────────────────────────

    # Admin Profile

    # ───────────────────────────────

    path('admin/profile/',profile.AdminProfile, name="AdminProfile"),
    path('admin/settings/',profile.AdminSettings, name="AdminSettings"),


    path('admin/invoice/',profile.AdminInvoice, name="AdminInvoice"),
    path("admin/invoice/popup/add/",profile.popup_add_product_to_invoice,name="popup_add_product_to_invoice"),



    # ───────────────────────────────

    # Dashboard

    # ───────────────────────────────
    path('dashboard/',dashboard.Dashboard, name="Dashboard"),


    # ───────────────────────────────

    # Inventory

    # ───────────────────────────────
    path('inventory/',inventory.InventoryHome, name="InventoryHome"),
    path('inventory/advanced-search/filter/',inventory.AdvancedSearchFilter, name="AdvancedSearchFilter"),


    # Categories
    path('inventory/categories/',inventory.Categories, name="Categories"),

    path('inventory/add-category/',inventory.AddCategory, name="AddCategory"),
    path('inventory/add-subcategory/',inventory.AddSubcategory, name="AddSubcategory"),
    path('inventory/delete-category/<str:cat_id>/',inventory.DeleteCategory, name="DeleteCategory"),
    path('inventory/edit-category/<str:cat_id>/',inventory.EditCategory, name="EditCategory"),
    path('inventory/subcategory/delete/<int:subcat_id>/', inventory.DeleteSubcategory, name='DeleteSubcategory'),

    path('inventory/get-subcategories/', inventory.get_subcategories, name='get_subcategories'),




    # Templates
    path('inventory/templates/',inventory.Templates, name="Templates"), 
    path('inventory/templates/add-template/',inventory.AddTemplate, name="AddTemplate"),
    path('inventory/templates/delete-template/<str:tem_id>/',inventory.DeleteTemplate, name="DeleteTemplate"),


    # Stocks
    path('inventory/stocks/',inventory.Stocks, name="Stocks"),
    path('inventory/stocks/add-stock/',inventory.AddStock, name="AddStock"),
    path('inventory/stocks/printinvoice/<str:invoice_id>/',inventory.PrintInvoice, name="PrintInvoice"),
    path('inventory/stocks/deletecredit/<str:invoice_id>/',inventory.DeleteCredit, name="DeleteCredit"),

    path('inventory/stocks/delete-stock/<str:stock_id>/',inventory.DeleteStock, name="DeleteStock"),




    # Products
    path('inventory/add-product/<str:tem_id>/',inventory.AddProduct, name="AddProduct"),
    path('inventory/edit-product/<str:prod_id>/',inventory.EditProduct, name="EditProduct"),
    path('inventory/products/delete/<str:prod_id>/', inventory.DeleteProduct, name='DeleteProduct'),

    
    path('inventory/products/<str:page>/<str:cat_id>/',inventory.Products, name="Products"),

    path("dashboard/review/toggle/", inventory.toggle_review_status, name="toggle_review_status"),
    path("dashboard/review/delete/", inventory.delete_review, name="delete_review"),



    # ───────────────────────────────

    # Merchants

    # ───────────────────────────────
    path('merchants/',merchants.MerchantHome, name="MerchantHome"),
    path('merchants/add-merchant/',merchants.AddMerchant, name="AddMerchant"),
    path('merchants/delete/<int:merchant_id>/', merchants.DeleteMerchant, name='DeleteMerchant'),

    path('merchants/view/<str:mtb_id>/',merchants.ViewMerchant, name="ViewMerchant"),
    path('merchants/settings/<str:mtb_id>/',merchants.SettingsMerchant, name="SettingsMerchant"),
    path('merchants/alerts/<str:mtb_id>/',merchants.AlertsMerchant, name="AlertsMerchant"),
    path('merchants/view/add-credit/<str:mtb_id>/',merchants.AddCreditMerchant, name="AddCreditMerchant"),
    path('merchants/view/printledger/<str:mtb_id>/',merchants.PrintLedger, name="PrintLedger"),


    # ───────────────────────────────

    # Clients

    # ───────────────────────────────
    path('clients/',clients.ClientHome, name="ClientHome"),
    path('clients/add-client/',clients.AddClient, name="AddClient"),
    path('clients/delete/<int:client_id>/', clients.DeleteClient, name='DeleteClient'),

    path('clients/view/<str:mtb_id>/',clients.ViewClient, name="ViewClient"),
    path('clients/settings/<str:mtb_id>/',clients.SettingsClient, name="SettingsClient"),
    path('clients/alerts/<str:mtb_id>/',clients.AlertsClient, name="AlertsClient"),
    path('clients/view/add-credit/<str:mtb_id>/',clients.AddCreditClient, name="AddCreditClient"),


    # ───────────────────────────────

    # Employees

    # ───────────────────────────────
    path('employees/',employees.EmployeeHome, name="MerchantHome"),
    path('employees/add-employee/',employees.AddEmployee, name="AddMerchant"),
    path('employees/delete/<int:employee_id>/', employees.DeleteEmployee, name='DeleteMerchant'),

    path('employees/view/<str:mtb_id>/',employees.ViewEmployee, name="ViewEmployee"),
    path('employees/settings/<str:mtb_id>/',employees.SettingsEmployee, name="SettingsEmployee"),
    path('employee/entries/delete/<int:entry_id>/',employees.delete_employee_entry,name="delete_employee_entry"),


    # ───────────────────────────────

    # Help & Reports

    # ───────────────────────────────

    path('help-reports/',views.HelpReports, name="HelpReports"),
    path("help-reports/read/<int:pk>/", views.HelpReportsRead, name="HelpReportsRead"),
    path("help-reports/delete/<int:pk>/", views.HelpReportsDelete, name="HelpReportsDelete"),

]
