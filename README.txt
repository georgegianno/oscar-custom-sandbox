This is a sample django-oscar project with some cool features. 
--> The basket works asynchronously.
--> The ranges have been customized. Adding or removing a parent product to a range always adds or removes its variants. If the option 'Standalone and parents only' is active, 
    then all variant products are removed from range. Standalone products are not affected. For every category added to a range (Included Categories) all its descendants are added 
    with all their products. For every category removed, all its descendants are removed as well. It works with 'Standalone and parents only' option smoothly. A search has been          added to the range dashboard page with title search and 'Show standalone and parents only' option that filters parents and standalone products. Those changes save a lot of          time when creating or updating ranges. 
--> How to test in Linux:
    pyenv local 3.8.6
    git clone https://github.com/georgegianno/oscar-custom-sandbox/
    python -m venv virtualenv
    source virtualenv/bin/activate
    make sandbox
    cd sandbox
    python manage.py runserver
    
