This is a sample django-oscar project with some cool features. 

Customizations:

--> The basket is updated to interact asynchronously to user actions(adding/removing/changing quantity/offers/vouchers).

-->  In product detail page a user can add or remove the product to their favorites. With every addition/removal, recommended products are generated based on the user's category
     preferences in relation to the time of the action.

-->  In dashboard category update page, there are three extra options for categories that contain products:
     1. Select subcategories and remove or add ALL of their products to the current category('select subcategories field').
     2. Order the products of the category('extra actions' button).
     3. Delete all the products of the category('extra actions' button).

--> The ranges have been customized. 
    1. Adding or removing a parent product to a range always adds or removes its children. 
    2. If the option 'Standalone and parents only' is active, then all child products are removed from range. Standalone products are not affected.
    3. For every category added to a range ('Included categories' field), all its descendants are added with all their products. For every category removed, all its descendants          are removed as well. It works with 'Standalone and parents only' option smoothly.
    4. A search has been added to the range dashboard page with title search option and 'Show standalone and parents only' option that filters parents and standalone products.
       There is an ordering option for products in range update page in dashboard and a button to view live the range page, which is missing from oscar.

--> Customers tab in dashboard has been updated to contain data for guest orders and options to export data for users, guests and all together, including their number of orders       and total money spent on orders with status 'Complete'.

--> How to test in Linux:
    set python version to 3.8.6
    git clone https://github.com/georgegianno/oscar-custom-sandbox/
    python -m venv virtualenv
    source virtualenv/bin/activate
    make sandbox
    run the command displayed in your terminal
    cd sandbox
    python manage.py runserver
    The superuser credentials: username:superuser, password:testing
    
