# Django-Oscar Custom Project

This is a sample Django-Oscar project with some cool features.

## Customizations

- **Basket Updates**:
    - The basket updates asynchronously in response to user actions, including adding/removing items, changing quantities, applying offers, and redeeming vouchers.

- **Product Detail Page**:
    - Users can add or remove products from their favorites.
    - Each addition or removal generates recommended products based on the user's category preferences and the timing of the action.

- **Dashboard Category Update Page**:
    - Three extra options are available for categories that contain products:
        1. **Select Subcategories**: Allows adding or removing all products in selected subcategories from the current category (available in the 'select subcategories' field).
        2. **Order Products**: Provides options to order products within the category (accessible via the 'extra actions' button).
        3. **Delete All Products**: Enables the deletion of all products in the category (also found under the 'extra actions' button).

- **Range Customizations**:
    1. Adding or removing a parent product in a range automatically includes or removes its child products.
    2. If the **'Standalone and parents only'** option is active, all child products are removed from the range, while standalone products remain unaffected.
    3. When a category is added to a range (in the 'Included categories' field), all its descendants and their products are also included. If removed, all descendants are excluded as well.
    4. The range dashboard page has new search and filter options, including title search and a 'Show standalone and parents only' filter, making it easier to manage categories and products. 
       - The range update page now includes an option to order products and a button to view the live range page, addressing a feature gap in the original Django-Oscar.

- **Customer Data in Dashboard**:
    - The Customers tab now includes data for guest orders and options to export user and guest data, individually or combined.
    - It displays the total number of orders and the cumulative spending for orders with a 'Complete' status.

- **Promo Offers**:
    - In the Offers tab in the dashboard, you will find the **'Promo offers'** feature.
    - A promotional offer allows you to give away a free product to any basket that meets specified conditions.
       - The gift product must be unpublished and priced at zero.
       - If the promo contains one gift, it will automatically be added to the basket when conditions are met.
       - If multiple gifts are available, a list of options will appear in the basket for the user to select from.
       - Each promo grants only one gift per user, but you can set up multiple promos with different conditions.
       - When the stock of a gift is zero, the next gift is added to the basket, if it exists, when visiting the basket or the checkout page.
       - Anytime a gift should not be in a basket for any reason (i.e. promo not active anymore), it is removed via middleware.
    - **Example**: To create a promo that adds a free gift to any basket with:
       - A total price above 50.00
       - More than 3 products, with at least 2 of them being books, but not a specific book
       - Includes a progress bar to show users how close they are to receiving their gift.
       
      To configure this promo:
       - **Promo range**: Make a range of gifts.
       - **Included range**: Make a range that includes Book category products.
       - **Excluded range**: Make a range that excludes the specific book.
       - **Minimum number of products**: Set to 3.
       - **Price threshold**: Set to 50.
       - **Show progress bar**: Enable this option.
       - **Active**: Enable this option.

    - **Note**: Ensure that the products within the selected category explicitly belong to that category, rather than only being assigned to subcategories.

    - **Sample Promo**: A simpler promo with 2 gifts and a 60.00 price threshold has been set up in the database for reference.

## How to Test in Linux

1. Set the Python version to 3.8.6.
2. Clone the repository from GitHub: `git clone https://github.com/georgegianno/oscar-custom-sandbox/`
3. Create a virtual environment: `python -m venv virtualenv`
4. Activate the virtual environment: `source virtualenv/bin/activate`
5. Run the setup by executing: `make sandbox`
6. Follow the command displayed in your terminal, then navigate to the sandbox directory: `cd sandbox`
7. Start the server with the command: `python manage.py runserver`

- **Superuser Credentials**:
   - Username: `superuser`
   - Password: `testing`
