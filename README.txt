This is a sample django-oscar project with some cool features. 

Customizations:

--> The basket is updated asynchronously(adding/removing/changing quantity).

-->  In product detail page a user can add or remove the product to their favorites. With every addition/removal, recommended products are generated based on the user's category
     preferences in relation to the time of the action.

--> In dashboard category update page, there is the option of ordering the products in this category. When this option is selected, the products of every descendant of this            category are added and can be ordered. It is an easy way to make products inherit their ancestors' categories without doing it manually. 

--> The ranges have been customized. Adding or removing a parent product to a range always adds or removes its variants. If the option 'Standalone and parents only' is active, 
    then all variant products are removed from range. Standalone products are not affected. For every category added to a range (Included Categories) all its descendants are          added with all their products. For every category removed, all its descendants are removed as well. It works with 'Standalone and parents only' option smoothly. A search has      been added to the range dashboard page with title search and 'Show standalone and parents only' option that filters parents and standalone products. Those changes save a lot      of time when creating or updating ranges. 

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
    
