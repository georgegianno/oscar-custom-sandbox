This is a sample django-oscar project with some cool features. 
--> The basket works asynchronously.
--> The ranges have been customized. Adding or removing a parent product to a range always adds or removes its variants. If the option 'Standalone and parents only' is active, 
    then all variant products are removed from range. Standalone products are not affected. For every category added to a range (Included Categories) all its descendants are added 
    with all their products. For every category removed, all its descendants are removed as well. It works with 'Standalone and parents only' option smoothly. Those changes save a lot of time when 
    creating or updating ranges. A search has been added to the range dashboard page with 'Show tandalone and parents only' option that filters parents and standalone products.
