Project 3: Financial Assets Application
=============

The Financial Assets Application shows a list of Asset Classes. Users can login to the application via Facebook to view existing Asset Classes and create new ones. Financial Assets are contained within each Asset Class and can be created, edited, or deleted by authenticated users.

**Steps to Run Application:**
1. Clone Project 3 - Item Catalog repository
2. Open the Command Line. 
3. Use cd in the Command Line and cd into the **Vagrant** directory.
4. Run "vagrant up".
5. Run "vagrant ssh" after step #4 completes.
6. cd into the **catalog** directory.
7. Run "python database_setup.py" to compile the Python code that creates the database for the application. 
8. Run "python seed_database.py" to create some default Asset Classes and Financial Assets in the application. 
9. Run "python project.py" to run the application on port 8000. 
10. Open a Web Browser. 
11. Visit http://localhost:8000/asset_classes/ or http://localhost:8000/ to view the application in the browser.
